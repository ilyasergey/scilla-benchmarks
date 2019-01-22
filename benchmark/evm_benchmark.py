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
from benchmark_plans import contracts_benchmark_plans, SENDER_ADDRESS, get_token_address


def setup_test(setup_plans, contract_address):
    for setup_plan in setup_plans:
        perform_transaction(contract_address, setup_plan)


def run_tests(address, tests):
    for test_plan in tests:
        test_name = test_plan['test_name']

        setup_plans = test_plan.get('setup_transactions')
        if setup_plans:
            print('Setting up `{}`...'.format(test_name))
            if callable(setup_plans):
                setup_plans()
            else:
                setup_test(setup_plans, address)
            print('Finished setting up `{}`.'.format(test_name))

        all_transactions = test_plan['transactions']
        matching_txns = filter(
            lambda tx: tx['function'].name == test_name, all_transactions)
        iterations = len(list(matching_txns))
        print('Running {} iterations of `{}` function'.format(
            iterations, test_name))

        execution_times = []
        iteration_counter = 0

        for txn_plan in all_transactions:
            is_matching_test = txn_plan['function'].name == test_name
            if is_matching_test:
                iteration_counter += 1
                if iteration_counter % 10 == 0:
                    print('Ran {} iterations'.format(iteration_counter))

            time_taken = perform_transaction(address, txn_plan)

            # there may be some transactions interleaved
            # so we only count the ones with the matching function name
            if is_matching_test:
                execution_times.append(time_taken)

        print('Ran {} iterations of {} function'.format(
            iterations, test_plan['test_name']))
        print('New database size: {:,} bytes'.format(measure_evm_data_size()))
        print('Median execution time: {0:.6f} ms'.format(
            median(execution_times)))
        print('Mean execution time: {0:.6f} ms'.format(
            mean(execution_times)))
        print()


def populate_evm_state(address, transactions):
    print(
        '\nPopulating EVM state with {} transactions...'.format(
            len(transactions)))
    for index, txn_plan in enumerate(transactions):
        if index % 10 == 0:
            print('Executed {} transactions'.format(index))
        perform_transaction(address, txn_plan)


def run_benchmark(contract_plan):
    # clear the EVM data directory
    if os.path.isdir(evm_data_dir):
        shutil.rmtree(evm_data_dir)

    before_deploy_function = contract_plan.get('before_deploy')
    if before_deploy_function:
        before_deploy_function()

    contract_path = os.path.join(
        contracts_dir, contract_plan['contract_filename'])
    bytecode = solc_compile_contract(
        contract_path, contract_plan['contract_name'])
    address = deploy_contract(bytecode, *contract_plan['constructor'])
    print('Contract deployed at:', address)
    print('Contract bytecode size: {:,} bytes'.format(
        len(bytecode.encode('utf-8'))))
    print('Initial EVM database size: {:,} bytes'.format(
        measure_evm_data_size()))

    after_deploy_function = contract_plan.get('after_deploy')
    if after_deploy_function:
        print('Running after_deploy function')
        after_deploy_function(address)

    populate_evm_state(address, contract_plan['transactions'])
    print('\nPopulated EVM database size: {:,} bytes\n'.format(
        measure_evm_data_size()))

    run_tests(address, contract_plan['tests'])
    print('Final EVM database size: {:,} bytes'.format(
        measure_evm_data_size()))


def main():
    for plan in contracts_benchmark_plans:
        run_benchmark(plan)


if __name__ == '__main__':
    main()
