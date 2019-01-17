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

from evm_tools import measure_evm_data_size, measure_gas_cost, solc_compile_contract,\
    get_value, generate_params, deploy_contract, perform_transaction, evm_data_dir,\
    contracts_dir
from benchmark_plans import contracts_benchmark_plans, SENDER_ADDRESS


def setup_test(setup_plans, contract_address):
    for setup_plan in setup_plans:
        args = generate_params(setup_plan['values'])
        caller = get_value(setup_plan['caller'])
        function = setup_plan['function']
        start = time.time()
        perform_transaction(caller, contract_address, function, *args)


def run_tests(address, tests):
    for test_plan in tests:
        test_name = test_plan['test_name']

        setup_plans = test_plan.get('setup_transactions')
        if setup_plans:
            print('Setting up `{}`...'.format(test_name))
            setup_test(setup_plans, address)
            print('Finished setting up `{}`.'.format(test_name))

        iterations = len(test_plan['transactions'])
        print('Running {} iterations of `{}` function'.format(
            iterations, test_name))

        execution_times = []

        for iteration in range(iterations):
            txn_plan = test_plan['transactions'][iteration]
            if iteration % 10 == 0:
                print('Ran {} iterations'.format(iteration))
            args = generate_params(txn_plan['values'])
            caller = get_value(txn_plan['caller'])
            function = txn_plan['function']
            block_timestamp = txn_plan.get('time', 0)
            amount = txn_plan.get('amount', 0)
            start = time.time()
            perform_transaction(caller, address, function,
                                *args, time=block_timestamp, amount=amount)
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
    for index, txn_plan in enumerate(transactions):
        if index % 10 == 0:
            print('Executed {} transactions'.format(index))
        caller = get_value(txn_plan['caller'])
        args = generate_params(txn_plan['values'])
        perform_transaction(caller, address, txn_plan['function'], *args)


def run_benchmark(contract_plan):
    contract_path = os.path.join(
        contracts_dir, contract_plan['contract_filename'])
    bytecode = solc_compile_contract(
        contract_path, contract_plan['contract_name'])
    address = deploy_contract(bytecode, *contract_plan['constructor'])
    print('Contract deployed at:', address)
    print('Contract bytecode size: {:,} bytes'.format(
        len(bytecode.encode('utf-8'))))

    populate_evm_state(address, contract_plan['transactions'])

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
