import re
import os
import binascii
import subprocess
from eth_abi import encode_abi
from utils import keccak256, generate_address,\
    get_addresses, get_directory_size
import uuid
import random
import shutil
import time
from statistics import median, mean
from benchmark_plans import contracts_benchmark_plans


GO_ROOT = os.environ['GOROOT']
evm_exec = os.path.join(GO_ROOT, 'evm')
# evm_deploy_exec = os.path.join(GO_ROOT, 'evm')
disasm_exec = os.path.join(GO_ROOT, 'disasm')

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, 'output')
evm_data_dir = os.path.join(current_dir, 'evm-data')
contracts_dir = os.path.join(current_dir, 'contracts')

SENDER_ADDRESS = '0xfaB8FcF1b5fF9547821B4506Fa0C35c68a555F90'
SENDER_PRIVKEY = '4bc95d997c4c700bb4769678fa8452c2f67c9348e33f6f32b824253ae29a5316'

devnull_file = open(os.devnull, 'w')


def solc_compile_contract(contract_path, contract_name):
    output_path = os.path.join(output_dir, contract_name+'.bin')
    subprocess.check_output(['solc', '--bin', '--optimize', '--overwrite',
                             '-o', output_dir, contract_path],
                            stderr=devnull_file)
    print('Compiled {} to {}'.format(contract_name, output_path))
    bytecode = None
    with open(output_path) as f:
        bytecode = f.read()
    return bytecode


def encode_args(types, values):
    hex_args = binascii.hexlify(encode_abi(types, values))
    return hex_args.decode('utf-8')


def deploy_contract(bytecode, *constructor_args):
    arg_types, arg_values = constructor_args
    if constructor_args:
        bytecode += encode_args(arg_types, arg_values)

    gas_cost = measure_gas_cost(bytecode)
    print('Total gas cost:', gas_cost)

    call_args = [evm_exec, '--code', bytecode, '--datadir',
                 evm_data_dir, '--from', SENDER_ADDRESS]
    deploy_output = subprocess.check_output(call_args, stderr=devnull_file)

    prefix = 'Contract Address: '
    prefix_pos = deploy_output.decode('utf-8').find(prefix)
    address_start_pos = prefix_pos+len(prefix)
    address_end_pos = address_start_pos + 40
    contract_address = deploy_output[address_start_pos:address_end_pos]

    return '0x'+contract_address.decode('utf-8')


def encode_input(function, *args):
    hex_args = encode_args(function.arg_types, args)
    return function.get_signature() + hex_args


def perform_transaction(address, function, *args):
    encoded_input = encode_input(function, *args)
    subprocess.check_output(
        [evm_exec, '--datadir', evm_data_dir, '--to', address,
         '--input', encoded_input, '--from', SENDER_ADDRESS],
        stderr=devnull_file)


def generate_random_params(arg_types):
    values = []
    for arg_type in arg_types:
        if arg_type == 'address':
            values.append(random.choice(get_addresses()))
        elif arg_type == 'string':
            values.append(str(uuid.uuid4()))
        else:
            values.append(random.randint(1, 100000))
    return values


def measure_evm_data_size():
    leveldb_dir = os.path.join(evm_data_dir, 'evm')
    data_size = get_directory_size(leveldb_dir)
    return data_size


def measure_gas_cost(bytecode):
    p = subprocess.Popen([evm_exec, '--debug', '--code', bytecode],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_output, debug_output = p.communicate()
    costs = re.compile('COST: (\d*)').findall(debug_output.decode('utf-8'))
    costs = [int(s) for s in costs]
    return sum(costs)


def run_tests(address, tests):
    for test_plan in tests:
        iterations = test_plan['iterations']
        function = test_plan['function']
        print('Running {} iterations of `{}` function'.format(
            iterations, function.name))

        execution_times = []

        for iteration in range(iterations):
            if iteration % 10 == 0:
                print('Ran {} iterations'.format(iteration))
            args = generate_random_params(function.arg_types)
            start = time.time()
            perform_transaction(address, function, *args)
            end = time.time()
            execution_times.append(end-start)

        print('Ran {} iterations of {} function'.format(
            iterations, function.name))
        print('New database size: {:,} bytes'.format(measure_evm_data_size()))
        print('Median execution time: {0:.6f} seconds'.format(
            median(execution_times)))
        print('Mean execution time: {0:.6f} seconds'.format(
            mean(execution_times)))
        print()


def populate_evm_state(address, transactions):
    print(
        '\nPopulating EVM state with {} transactions...'.format(
            len(transactions)))
    for index, tx_plan in enumerate(transactions):
        if index % 10 == 0:
            print('Executed {} transactions'.format(index))
        perform_transaction(address, *tx_plan)


def run_benchmark(contract_plan):
    contract_path = os.path.join(
        contracts_dir, contract_plan['contract_filename'])
    bytecode = solc_compile_contract(
        contract_path, contract_plan['contract_name'])
    address = deploy_contract(bytecode, *contract_plan['constructor'])
    print('Contract deployed at:', address)
    print('Contract bytecode size: {:,} bytes'.format(
        len(bytecode.encode('utf-8'))))

    txn_limit = contract_plan['transactions_limit']
    populate_evm_state(address, contract_plan['transactions'][:txn_limit])

    print('\nInitial EVM database size: {:,} bytes\n'.format(
        measure_evm_data_size()))
    run_tests(address, contract_plan['tests'])
    print('Final EVM database size: {:,} bytes'.format(
        measure_evm_data_size()))


def main():
    # clear the EVM data directory
    if os.path.isdir(evm_data_dir):
        shutil.rmtree(evm_data_dir)
    for plan in contracts_benchmark_plans:
        run_benchmark(plan)


if __name__ == '__main__':
    main()
