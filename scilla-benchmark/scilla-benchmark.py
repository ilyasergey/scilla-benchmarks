import os
import sys
import time
import json
import subprocess
from benchmark_plans import get_benchmark_plans


scilla_runner_exec = '/home/scilla/bin/scilla/bin/scilla-runner'
current_dir = os.path.dirname(os.path.realpath(__file__))
contracts_dir = os.path.join(current_dir, 'contracts')
blockchain_json = os.path.join(contracts_dir, 'blockchain.json')
output_dir = os.path.join(current_dir, 'output')
message_json = os.path.join(contracts_dir, 'message.json')


def create_message_file(tag, amount, sender, params):
    message_json = {
        "_tag": tag,
        "_amount": str(amount),
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


def run_test(contract_name, transaction):
    test_dir = os.path.join(contracts_dir, contract_name)
    contract_path = os.path.join(test_dir, 'contract.scilla')
    init_json = os.path.join(test_dir, 'init.json')
    state_json = os.path.join(test_dir, 'state.json')
    output_filepath = os.path.join(output_dir, contract_name)

    tag = transaction['transition']
    params = transaction['params']
    amount = transaction['amount']
    sender = transaction['sender']
    create_message_file(tag, amount, sender, params)

    command = [scilla_runner_exec, '-init', init_json, '-istate', state_json,
               '-iblockchain', blockchain_json, '-imessage', message_json,
               '-o', output_filepath, '-i', contract_path, '-libdir', 'src/stdlib']
    start = time.time()
    subprocess.call(command)
    time_taken = end - start

    return time_taken


def run_benchmark(no_of_state_entries, iterations=100):
    benchmark_plans = get_benchmark_plans(no_of_state_entries, iterations)
    for contract_plan in benchmark_plans:
        contract_name = contract_plan['contract']
        test_plans = contract_plan['tests']
        create_state_file(contract_plan['state'])

        for test_plan in test_plans:
            execution_times = []
            test_name = test_plan['test_name']
            transactions = test_plan['transactions']
            iterations = len(transactions)
            print('Running {} iterations of `{}` function'.format(
                iterations, test_name))

            for iteration, transaction in enumerate(transactions):
                if iteration % 10 == 0:
                    print('Ran {} iterations'.format(iteration))
                time_taken = run_test(contract_name, transaction)
                execution_times.append(time_taken)

            print('Ran {} iterations of {} function'.format(
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
