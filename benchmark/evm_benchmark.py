import os
import binascii
import subprocess
from eth_abi import encode_abi
from Crypto.Hash import keccak


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


def keccak256(string):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(string)
    return keccak_hash.hexdigest()


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

    call_args = [evm_exec, '--code', bytecode, '--datadir', evm_data_dir, '--from', SENDER_ADDRESS]
    deploy_output = subprocess.check_output(call_args)
    print(deploy_output.decode('utf-8'))

    prefix = 'Contract Address: '
    prefix_pos = deploy_output.decode('utf-8').find(prefix)
    address_start_pos = prefix_pos+len(prefix)
    address_end_pos = address_start_pos + 40
    contract_address = deploy_output[address_start_pos:address_end_pos]

    return '0x'+contract_address.decode('utf-8')


def encode_input(function_name, *args):
    signature = keccak256(function_name.encode('utf-8'))[:8]
    arg_types = function_name[function_name.find('(')+1:function_name.find(')')]
    arg_types = ','.split(arg_types)
    hex_args = encode_args(arg_types, args)
    return signature + hex_args


def perform_transaction(address, function_name, *args):
    encoded_input = encode_input(function_name, *args)
    print('Encoded input', encoded_input)
    subprocess.call(
        [evm_exec, '--datadir', evm_data_dir, '--to', address, '--input', encoded_input, '--from', SENDER_ADDRESS])


def run_benchmark(contract_plan):
    contract_path = os.path.join(
        contracts_dir, contract_plan['contract_filename'])
    bytecode = solc_compile_contract(
        contract_path, contract_plan['contract_name'])
    address = deploy_contract(bytecode, *contract_plan['constructor'])
    print('Contract deployed at', address)

    for tx_plan in contract_plan['transactions']:
        perform_transaction(address, *tx_plan)


def main():
    contracts_plans = [
        #{
        #    'contract_filename': 'add.sol',
        #    'contract_name': 'Addition',
        #    'constructor': (),
        #    'transactions': [
        #        ('add(int256,int256)', 4, 5)
        #    ]
        #},
        {
            'contract_filename': 'token.sol',
            'contract_name': 'TokenERC20',
            'constructor': (('uint256', 'string', 'string'), (1000000, 'Test', 'TEST')),
            'transactions': [
                #('transfer(address,uint256)', '3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE', 1000),
            ]
        }

    ]
    for plan in contracts_plans:
        run_benchmark(plan)


if __name__ == '__main__':
    main()

