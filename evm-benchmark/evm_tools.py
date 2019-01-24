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
# evm_deploy_exec = os.path.join(GO_ROOT, 'evm')
disasm_exec = os.path.join(GO_ROOT, 'disasm')

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, 'output')
evm_data_dir = os.path.join(current_dir, 'evm-data')
contracts_dir = os.path.join(current_dir, 'contracts')

devnull_file = open(os.devnull, 'w')
ROOT_HASH = '0000000000000000000000000000000000000000000000000000000000000000'


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
    hex_args = binascii.hexlify(encode_abi(types, values))
    return hex_args.decode('utf-8')


def deploy_contract(bytecode, *constructor_args):
    if constructor_args:
        arg_types, arg_values = constructor_args
        arg_values = generate_params(arg_values)
        bytecode += encode_args(arg_types, arg_values)

    call_args = None
    if len(bytecode) > 80000:
        intermediate_path = os.path.join(output_dir, 'intermediate.bin')
        with open(intermediate_path, 'w') as f:
            f.write(bytecode)
        call_args = [evm_exec, '--file', intermediate_path, '--datadir',
                     evm_data_dir, '--from', SENDER_ADDRESS]
    else:
        call_args = [evm_exec, '--code', bytecode, '--datadir',
                     evm_data_dir, '--from', SENDER_ADDRESS]
    deploy_output = subprocess.check_output(
        call_args, stderr=devnull_file)

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
               '--time', str(time), '--value', str(amount), '--sysstat']
    if root_hash:
        command += ['--root', root_hash]
    output = subprocess.check_output(command, stderr=devnull_file)
    match = re.search(b'vm took (\d*\.?\d*)', output)
    time_taken = float(match[1])  # remove ms from match
    return time_taken


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
    time_taken = perform_transaction_(caller, address, function,
                                      *args, time=block_timestamp,
                                      amount=amount, root_hash=root_hash)
    return time_taken


def get_current_root_hash():
    command = [evm_exec, '--datadir', evm_data_dir]
    output = subprocess.check_output(command, stderr=devnull_file)
    match = re.search(b'Loading root hash (.*)', output)
    return match[1]


def deploy_contract_with_name(path, name, *args):
    contract_path = os.path.join(
        contracts_dir, path)
    bytecode = solc_compile_contract(
        contract_path, name)
    address = deploy_contract(bytecode, *args)
    return address


def deploy_etheremon_database_contract():
    contract_path = os.path.join(
        contracts_dir, 'etheremon-data.sol')
    bytecode = solc_compile_contract(
        contract_path, 'EtheremonDataBase')
    address = deploy_contract(bytecode)
    return address


def deploy_token(iterations):
    types = ('uint256', 'string', 'string')
    args = (1000000, 'TEST', 'TEST')
    token_address = deploy_contract_with_name(
        'fungible-token.sol', 'ERC20', *(types, args))

    print('Deployed token contract at', token_address)
    print('Creating token transfers...')

    # for iteration in range(iterations):
    #     user_address = addresses[iteration]
    #     transaction = {
    #         'function': ContractFunction('transfer', ('address', 'uint256')),
    #         'values': (user_address, 100),
    #         'caller': SENDER_ADDRESS,
    #     }
    #     perform_transaction(token_address, transaction)

    return token_address


def approve_token_spend(token_address, spent_address, spender_address, amount):
    types = ('address', 'uint256')
    args = (spender_address, amount)
    perform_transaction(token_address, {
        'function': ContractFunction('approve', types),
        'values': args,
        'caller': spent_address
    })
