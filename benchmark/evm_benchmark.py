import os
import binascii
import subprocess
from eth_abi import encode_abi
from utils import keccak256, generate_address,\
    get_addresses, get_directory_size
import uuid
import random
import time
from statistics import median, mean


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


def solc_compile_contract(contract_path, contract_name):
    output_path = os.path.join(output_dir, contract_name+'.bin')
    subprocess.call(['solc', '--bin-runtime', '--optimize', '--overwrite',
                     '-o', output_dir, contract_path])
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

    call_args = [evm_exec, '--code', bytecode, '--datadir',
                 evm_data_dir, '--from', SENDER_ADDRESS]
    deploy_output = subprocess.check_output(call_args)

    prefix = 'Contract Address: '
    prefix_pos = deploy_output.decode('utf-8').find(prefix)
    address_start_pos = prefix_pos+len(prefix)
    address_end_pos = address_start_pos + 40
    contract_address = deploy_output[address_start_pos:address_end_pos]

    return '0x'+contract_address.decode('utf-8')


def encode_input(function_name, *args):
    signature = keccak256(function_name.encode('utf-8'))[:8]
    arg_types = function_name[function_name.find(
        '(')+1:function_name.find(')')]
    arg_types = arg_types.split(',')
    hex_args = encode_args(arg_types, args)
    return signature + hex_args


def perform_transaction(address, function, *args):
    encoded_input = encode_input(function.get_signature(), *args)
    subprocess.call(
        [evm_exec, '--datadir', evm_data_dir, '--to', address,
         '--input', encoded_input, '--from', SENDER_ADDRESS])


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


def run_tests(address, tests):
    for test_plan in tests:
        iterations = test_plan['iterations']
        function = test_plan['function']
        print('Running {} iterations of {} function'.format(
            iterations, function.name))

        execution_times = []

        for iteration in range(iterations):
            args = generate_random_params(function.arg_types)
            start = time.time()
            perform_transaction(address, function, args)
            end = time.time()
            execution_times.append(end-start)

        print('Ran {} iterations of {} function'.format(
            iterations, function.name))
        print('New database size: {}'.format(measure_evm_data_size()))
        print('Median execution time: {}'.format(median(execution_times)))
        print('Mean execution time: {}'.format(mean(execution_times)))


def run_benchmark(contract_plan):
    contract_path = os.path.join(
        contracts_dir, contract_plan['contract_filename'])
    bytecode = solc_compile_contract(
        contract_path, contract_plan['contract_name'])
    address = deploy_contract(bytecode, *contract_plan['constructor'])
    print('Contract deployed at', address)

    # populating the contract state
    for tx_plan in contract_plan['transactions']:
        perform_transaction(address, *tx_plan)

    print('Initial EVM database size: {}'.format(measure_evm_data_size()))
    run_tests(address, contract_plan['tests'])
    print('Final EVM database size: {}'.format(measure_evm_data_size()))


class ContractFunction():
    def __init__(self, name, arg_types):
        self.name = name
        self.arg_types = arg_types

    def get_signature(self):
        name_with_args = '{}({})'.format(self.name, ','.join(self.arg_types))
        signature = keccak256(name_with_args.encode('utf-8'))[:8]
        return signature


def main():
    total_token_supply = 1000000 * 10**16
    contracts_benchmark_plans = [
        # {
        #    'contract_filename': 'add.sol',
        #    'contract_name': 'Addition',
        #    'constructor': (),
        #    'transactions': [
        #        ('add(int256,int256)', 4, 5)
        #    ]
        # },
        {
            'contract_filename': 'token.sol',
            'contract_name': 'TokenERC20',
            'constructor': (
                ('uint256', 'string', 'string'),
                (total_token_supply, 'Test', 'TEST')),
            'transactions': [
                (
                    ContractFunction('transfer', ('address', 'uint256')),
                    addr, 1*(10**16)
                )
                for addr in get_addresses()
            ],
            'tests': [
                {
                    'function': ContractFunction(
                        'transfer', ('address', 'uint256'))
                    'iterations': 100
                },
                {
                    'function': ContractFunction('burn', ('uint256'))
                    'iterations': 100
                },
                {
                    'function': ContractFunction(
                        'approve', ('address', 'uint256'))
                    'iterations': 100
                },
            ]
        }

    ]
    for plan in contracts_benchmark_plans:
        run_benchmark(plan)


if __name__ == '__main__':
    main()
