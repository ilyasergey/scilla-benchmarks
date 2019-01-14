import os
import binascii
import subprocess
from Crypto.Hash import keccak


GO_ROOT = os.environ['GOROOT']
evm_exec = os.path.join(GO_ROOT, 'evm')
# evm_deploy_exec = os.path.join(GO_ROOT, 'evm')
disasm_exec = os.path.join(GO_ROOT, 'disasm')

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, 'output')
evm_data_dir = os.path.join(current_dir, 'evm-data')
contracts_dir = os.path.join(current_dir, 'contracts')


def keccak256(string):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(string)
    return keccak_hash.hexdigest()


def solc_compile_contract(contract_path, contract_name):
    output_path = os.path.join(output_dir, contract_name+'.bin')
    subprocess.call(['solc', '--bin', '--optimize', '--overwrite',
                     '-o', output_path, contract_path])
    bytecode = None
    with open(output_path) as f:
        bytecode = f.read()
    return bytecode


# def generate_deploy_bytecode(bytecode):


def deploy_contract(bytecode):
    deploy_output = subprocess.check_output(
        [evm_exec, '--code', bytecode, '--datadir', evm_data_dir])
    prefix = 'Contract Address: '
    prefix_pos = deploy_output.find(prefix)
    address_start_pos = prefix_pos+len(prefix)
    address_end_pos = address_start_pos + 40
    contract_address = deploy_output[address_start_pos:address_end_pos+1]
    return contract_address


def encode_input(function_name, *args):
    signature = keccak256(function_name)[:8]
    hex_args = ''

    for arg in args:
        hex_arg = None
        if isinstance(arg, str):
            hex_arg = binascii.hexlify(arg)
        elif isinstance(arg, int):
            hex_arg = hex(arg)[2:].zfill(64)
        hex_args += hex_arg

    return signature + hex_args


def perform_transaction(address, function_name, *args):
    encoded_input = encode_input(function_name, args)
    subprocess.call(
        [evm_exec, '--datadir', evm_data_dir, '--to', address, '--input', encoded_input])


def run_benchmark(contract_plan):
    contract_path = os.path.join(
        contracts_dir, contract_plan['contract_filename'])
    bytecode = solc_compile_contract(
        contract_path, contract_plan['contract_name'])
    address = deploy_contract(bytecode)

    for tx_plan in contract_plan['transactions']:
        perform_transaction(address, *tx_plan)


def main():
    contracts_plans = [
        {
            'contract_filename': 'add.sol',
            'contract_name': 'Addition',
            'transactions': [
                ('add', 4, 5)
            ]
        }

    ]
    for plan in contracts_plans:
        run_benchmark(plan)


if __name__ == '__main__':
    main()
