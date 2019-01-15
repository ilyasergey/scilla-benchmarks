import os
import binascii
import subprocess
from eth_abi import encode_abi
from utils import keccak256, generate_address, get_addresses


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


def encode_input(function, *args):
    hex_args = encode_args(function.arg_types, args)
    return function.get_signature() + hex_args


def perform_transaction(address, function, *args):
    encoded_input = encode_input(function, *args)
    subprocess.call(
        [evm_exec, '--datadir', evm_data_dir, '--to', address, '--input', encoded_input, '--from', SENDER_ADDRESS])


def run_test(test_plan):
    pass


def run_tests(address, tests):
    for test_plan in tests:
        perform_transaction()


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

    # run_tests(address, contract_plan['tests'])


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
    contracts_plans = [
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
            'constructor': (('uint256', 'string', 'string'), (total_token_supply, 'Test', 'TEST')),
            'transactions': [
                (ContractFunction('transfer', ('address', 'uint256')), addr, 1*(10**16))
                for addr in get_addresses()
            ],
            'tests': [
                {
                    'function': ContractFunction('transfer', ('address', 'uint256')),
                    'iterations': 100
                },
                {
                    'function': ContractFunction('burn', ('uint256')),
                    'iterations': 100
                },
                {
                    'function': ContractFunction('approve', ('address', 'uint256')),
                    'iterations': 100
                },
            ]
        }

    ]
    for plan in contracts_plans:
        run_benchmark(plan)


if __name__ == '__main__':
    main()
