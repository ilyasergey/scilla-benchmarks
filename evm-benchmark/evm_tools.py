import re
import os
import binascii
import subprocess
from eth_abi import encode_abi
from utils import keccak256, generate_address,\
    get_addresses, get_directory_size, SENDER_ADDRESS, ContractFunction,\
    addresses
import uuid
import random
import shutil
import time
from statistics import median, mean
from collections.abc import Iterable


GO_ROOT = os.environ['GOROOT']
evm_exec = os.path.join(GO_ROOT, 'evm')
evm_deploy_exec = os.path.join(GO_ROOT, 'evm-deploy')
disasm_exec = os.path.join(GO_ROOT, 'disasm')

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, 'output')
evm_start_data_dir = os.path.join(current_dir, 'evm-data-start')
evm_data_dir = os.path.join(current_dir, 'evm-data')
contracts_dir = os.path.join(current_dir, 'contracts')

devnull_file = open(os.devnull, 'w')
ROOT_HASH = '0000000000000000000000000000000000000000000000000000000000000000'
BYTECODE_MAX_LEN = 80000


def measure_evm_data_size():
    leveldb_dir = os.path.join(evm_data_dir, 'evm')
    data_size = get_directory_size(leveldb_dir)
    return data_size


def solc_compile_contract(contract_path, contract_name):
    output_path = os.path.join(output_dir, contract_name+'.bin')
    subprocess.call(['solc', '--bin', '--optimize', '--overwrite',
                             '-o', output_dir, contract_path],)
    # stderr=devnull_file)
    print('Compiled {} to {}'.format(contract_name, output_path))
    bytecode = None
    with open(output_path) as f:
        bytecode = f.read()
    return bytecode


def get_value(value_function, address=None):
    if callable(value_function):
        if address:
            return value_function(address)
        return value_function()
    elif isinstance(value_function, list):
        return [get_value(v) for v in value_function]
    else:
        return value_function


def generate_params(value_functions, address=None):
    values = [get_value(v, address=address) for v in value_functions]
    return values


def encode_args(types, values):
    abi = encode_abi(types, values)
    hex_args = binascii.hexlify(abi)
    return hex_args.decode('utf-8')


def write_to_intermediate_file(bytecode):
    intermediate_path = os.path.join(output_dir, 'intermediate.bin')
    with open(intermediate_path, 'w') as f:
        f.write(bytecode)
    return intermediate_path


def create_deployment_bytecode(bytecode):
    call_args = None

    if len(bytecode) > BYTECODE_MAX_LEN:
        intermediate_path = write_to_intermediate_file(bytecode)
        echo = subprocess.Popen(
            ('echo', intermediate_path), stdout=subprocess.PIPE)
        call_args = [evm_deploy_exec]
    else:
        echo = subprocess.Popen(('echo', bytecode), stdout=subprocess.PIPE)
        call_args = [evm_deploy_exec]
    deploy_bytecode = subprocess.check_output(call_args, stdin=echo.stdout)
    return deploy_bytecode.strip().decode('utf-8')


def deploy_contract(bytecode, *constructor_args, dirname=evm_data_dir):
    start = time.time()
    if constructor_args:
        arg_types, arg_values = constructor_args
        arg_values = generate_params(arg_values)
        bytecode += encode_args(arg_types, arg_values)
    print('Encoding params', time.time()-start)

    bytecode = create_deployment_bytecode(bytecode)

    start = time.time()
    call_args = None
    if len(bytecode) > BYTECODE_MAX_LEN:
        intermediate_path = write_to_intermediate_file(bytecode)
        call_args = [evm_exec, '--file', intermediate_path, '--datadir',
                     dirname, '--from', SENDER_ADDRESS, '--nojit']
    else:
        call_args = [evm_exec, '--code', bytecode, '--datadir',
                     dirname, '--from', SENDER_ADDRESS, '--nojit']
    print('Write bytecode to file', time.time()-start)

    start = time.time()
    deploy_output = subprocess.check_output(
        call_args)
    # print(deploy_output)
    print('Deploy to EVM', time.time()-start)

    prefix = 'Contract Address: '
    prefix_pos = deploy_output.decode('utf-8').find(prefix)
    address_start_pos = prefix_pos+len(prefix)
    address_end_pos = address_start_pos + 40
    contract_address = deploy_output[address_start_pos: address_end_pos]

    return '0x'+contract_address.decode('utf-8')


def encode_input(function, *args):
    hex_args = encode_args(function.arg_types, args)
    return function.get_signature() + hex_args


def perform_transaction_(from_address, to_address, function,
                         *args, time=0, amount=0, root_hash=None):
    encoded_input = encode_input(function, *args)
    command = [evm_exec, '--datadir', evm_data_dir, '--to', to_address,
               '--input', encoded_input, '--from', from_address,
               '--time', str(time), '--value', str(amount), '--sysstat',
               '--nojit'
               ]
    if root_hash:
        command += ['--root', root_hash]
    output = subprocess.check_output(command, stderr=devnull_file)
    exec_time = float(re.search(b'vm took (\\d*\\.?\\d*)', output)[1])
    init_time = float(re.search(b'Init: (\\d*)', output)[1])
    io_time = float(re.search(b'IO: (\\d*)', output)[1])

    return exec_time, init_time, io_time


def measure_gas_cost(bytecode):
    p = subprocess.Popen([evm_exec, '--debug', '--code', bytecode],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_output, debug_output = p.communicate()
    costs = re.compile('COST: (\d*)').findall(debug_output.decode('utf-8'))
    costs = [int(s) for s in costs]
    return sum(costs)


def perform_transaction(address, txn_plan, root_hash=None):
    args = generate_params(txn_plan['values'], address=address)
    caller = get_value(txn_plan['caller'])
    function = txn_plan['function']
    block_timestamp = txn_plan.get('time', 0)
    amount = txn_plan.get('amount', 0)
    exec_time, init_time, io_time = perform_transaction_(caller, address, function,
                                                         *args, time=block_timestamp,
                                                         amount=amount, root_hash=root_hash)
    total_time = exec_time + init_time + io_time
    return total_time, exec_time, init_time, io_time


def get_current_root_hash():
    command = [evm_exec, '--datadir', evm_data_dir]
    output = subprocess.check_output(command, stderr=devnull_file)
    match = re.search(b'Loading root hash (.*)', output)
    return match[1]
