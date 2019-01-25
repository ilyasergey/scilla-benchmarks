import os
import re
import sys
import time
import json
import uuid
import subprocess
from statistics import median, mean
from benchmark_plans import get_benchmark_plans


scilla_dir = '/home/scilla'
scilla_runner_exec = os.path.join(scilla_dir, 'bin', 'scilla-runner')
std_lib = os.path.join(scilla_dir, 'src', 'stdlib')
current_dir = os.path.dirname(os.path.realpath(__file__))
contracts_dir = os.path.join(current_dir, 'contracts')
blockchain_json = os.path.join(contracts_dir, 'blockchain.json')
output_dir = os.path.join(current_dir, 'output')


def create_message_file(contract_name, tag, amount, sender, params):
    message_json = os.path.join(contracts_dir, contract_name, 'message.json')
    message = {
        "_tag": tag,
        "_amount": amount,
        "_sender": sender,
        "params": params
    }
    with open(message_json, 'w') as f:
        json.dump(message, f)


def create_state_file(contract_name, state):
    state_path = os.path.join(contracts_dir, contract_name, 'state.json')
    with open(state_path, 'w') as f:
        json.dump(state, f)
    return state_path


def run_test(contract_name, transaction, blockchain_json=blockchain_json):
    test_dir = os.path.join(contracts_dir, contract_name)
    contract_path = os.path.join(test_dir, 'contract.scilla')
    init_json = os.path.join(test_dir, 'init.json')
    state_json = os.path.join(test_dir, 'state.json')
    message_json = os.path.join(test_dir, 'message.json')
    output_filepath = os.path.join(output_dir, contract_name)

    tag = transaction['transition']
    params = transaction['params']
    amount = transaction['amount']
    sender = transaction['sender']
    create_message_file(contract_name, tag, amount, sender, params)

    command = [scilla_runner_exec, '-init', init_json, '-istate', state_json,
               '-iblockchain', blockchain_json, '-imessage', message_json,
               '-o', output_filepath, '-i', contract_path, '-libdir', std_lib,
               '-gaslimit', '10000000']
    output = subprocess.check_output(command)
    match = re.search(b'time:(.*)', output)
    time_taken = float(match[1]) * 1000
    return time_taken


def run_benchmark(no_of_state_entries, iterations=100):
    benchmark_plans = get_benchmark_plans(no_of_state_entries, iterations)
    for contract_plan in benchmark_plans:
        contract_name = contract_plan['contract']
        test_plans = contract_plan['tests']
        print('Using {:,} state entries...'.format(no_of_state_entries))
        create_state_file(contract_name, contract_plan['state'])

        for test_plan in test_plans:
            execution_times = []
            test_name = test_plan['test_name']
            transactions = test_plan['transactions']
            blockchain_filename = test_plan.get('blockchain')
            iterations = len(transactions)
            print('Running {} iterations of `{}` function'.format(
                iterations, test_name))

            bjson = blockchain_json
            if blockchain_filename:
                bjson = os.path.join(
                    contracts_dir, blockchain_filename)

            if iterations == 0:
                raise Exception(
                    'Transactions is empty, addresses generated is not enough')

            for iteration, transaction in enumerate(transactions):
                if iteration % 10 == 0:
                    print('Ran {} iterations'.format(iteration))
                time_taken = run_test(
                    contract_name, transaction, blockchain_json=bjson)
                execution_times.append(time_taken)

            print('Using {:,} state entries...'.format(no_of_state_entries))
            print('Ran {} iterations of `{}` function'.format(
                iterations, test_name))
            # print('New database size: {:,} bytes'.format(
            #     calculate_all_db_key_value_sizes()))
            print('Median execution time: {0:.6f} ms'.format(
                median(execution_times)))
            print('Mean execution time: {0:.6f} ms'.format(
                mean(execution_times)))
            print()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        run_benchmark(int(sys.argv[1]), int(sys.argv[2]))
    else:
        run_benchmark(int(sys.argv[1]))
