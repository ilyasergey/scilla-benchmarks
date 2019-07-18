import os
import re
import sys
import time
import json
import uuid
import pprint
import subprocess
from statistics import median, mean
from benchmark_plans import get_benchmark_plans
from collections import Counter


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

    src_size = os.path.getsize(contract_path)
    print('Contract size: {} bytes'.format(src_size))

    command = [scilla_runner_exec, '-init', init_json, '-istate', state_json,
               '-iblockchain', blockchain_json, '-imessage', message_json,
               '-o', output_filepath, '-i', contract_path, '-libdir', std_lib,
               '-gaslimit', '100000000', '-disable-pp-json', '-disable-validate-json']
    output = subprocess.check_output(command)

    # time taken to parse JSON into state map
    init_time = float(re.search(b'init:(.*)', output)[1])*1000

    # time taken to actually execute Scilla code
    exec_time = float(re.search(b'exec:(.*)', output)[1])*1000

    # time taken to serialize Scilla types into JSON types
    osj = float(re.search(b'output_state_json:(.*)', output)[1])*1000
    omj = float(re.search(b'output_message_json:(.*)', output)[1])*1000
    oej = float(re.search(b'output_event_json:(.*)', output)[1])*1000
    serialize_time = osj + omj + oej

    # time taken to write JSON to a file
    write_time = float(re.search(b'write_to_file:(.*)', output)[1])*1000

    all_time_taken = init_time + exec_time + serialize_time + write_time

    return all_time_taken, init_time, exec_time, serialize_time, write_time


def run_single_test(contract_name, no_of_state_entries):
    benchmark_plans = get_benchmark_plans(no_of_state_entries, 1)
    executed_once = False

    for contract_plan in benchmark_plans:
        try:
            create_state_file(contract_name, contract_plan['state'])
        except:
            print("There is no contract named '{}'".format(contract_name))
            print(
                "The available contracts are: fungible-token, nonfungible-token, auction, crowdfunding")
            return

        if contract_plan['contract'] != contract_name:
            continue

        executed_once = True
        test_plans = contract_plan['tests']

        for test_plan in test_plans:
            transactions = test_plan['transactions']
            one_transaction = transactions[0]

            all_time_taken, init_time, exec_time, \
                serialize_time, write_time = run_test(
                    contract_name, one_transaction
                )

            print('Using {:,} state entries in {} contract'.format(
                no_of_state_entries, contract_name))
            print('Total time: {0:.6f} ms'.format(
                all_time_taken))
            print('    init time: {0:.6f} ms'.format(
                init_time))
            print('    exec time: {0:.6f} ms'.format(
                exec_time))
            print('    serialize time: {0:.6f} ms'.format(
                serialize_time))
            print('    write time: {0:.6f} ms'.format(
                write_time))
            print()

    if not executed_once:
        print("There is no contract named '{}'".format(contract_name))
        print("The available contracts are: fungible-token, nonfungible-token, auction, crowdfunding")


def run_benchmark(no_of_state_entries, iterations=100):
    benchmark_plans = get_benchmark_plans(no_of_state_entries, iterations)
    for contract_plan in benchmark_plans:
        contract_name = contract_plan['contract']
        test_plans = contract_plan['tests']
        print()
        print('Using {:,} state entries...'.format(no_of_state_entries))
        create_state_file(contract_name, contract_plan['state'])

        for test_plan in test_plans:
            init_times = []
            exec_times = []
            serialize_times = []
            write_times = []
            total_times = []

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

            # test_dir = os.path.join(contracts_dir, contract_name)
            # contract_path = os.path.join(test_dir, 'contract.scilla')
            # with open(contract_path) as f:
            #     content = f.read()
            #     print('Contract {} size:'.format(contract_name), len(content))

            if iterations == 0:
                raise Exception(
                    'Transactions is empty, addresses generated is not enough')

            for iteration, transaction in enumerate(transactions):
                if iteration % 10 == 0:
                    print('Ran {} iterations'.format(iteration))

                all_time_taken, init_time, exec_time, \
                    serialize_time, write_time = run_test(
                        contract_name, transaction, blockchain_json=bjson
                    )

                init_times.append(init_time)
                exec_times.append(exec_time)
                serialize_times.append(serialize_time)
                write_times.append(write_time)
                total_times.append(all_time_taken)

            print('Using {:,} state entries in {} contract'.format(
                no_of_state_entries, contract_name))
            print('Ran {} iterations of `{}` function'.format(
                iterations, test_name))
            # print('New database size: {:,} bytes'.format(
            #     calculate_all_db_key_value_sizes()))
            print('Median total time: {0:.6f} ms'.format(
                median(total_times)))
            # print('Mean execution time: {0:.6f} ms'.format(
            #     mean(exec_times)))
            print('    Median init time: {0:.6f} ms'.format(
                median(init_times)))
            print('    Median exec time: {0:.6f} ms'.format(
                median(exec_times)))
            print('    Median serialize time: {0:.6f} ms'.format(
                median(serialize_times)))
            print('    Median write time: {0:.6f} ms'.format(
                median(write_times)))
            print()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Invalid number of arguments, wanted 3')
        sys.exit()

    if sys.argv[1] == 'multi':
        run_benchmark(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == 'single':
        run_single_test(sys.argv[2], int(sys.argv[3]))
