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

    command = [scilla_runner_exec, '-init', init_json, '-istate', state_json,
               '-iblockchain', blockchain_json, '-imessage', message_json,
               '-o', output_filepath, '-i', contract_path, '-libdir', std_lib,
               '-gaslimit', '100000000', '-disable-pp-json', '-disable-validate-json']
    output = subprocess.check_output(command)
    # print(output.decode('utf-8'))
    # output = subprocess.call(command)
    all_time_match = re.search(b'time:(.*)', output)
    output_state_match = re.search(b'output_state_json:(.*)', output)
    mapvalues = [float(i)*1000 for i in re.compile(
        'map:(.*)').findall(output.decode('utf-8'))]
    kjson = re.compile('kjson:(.*)').findall(output.decode('utf-8'))
    kjson = [float(i)*1000 for i in kjson]
    vjson = re.compile('vjson:(.*)').findall(output.decode('utf-8'))
    vjson = [float(i)*1000 for i in vjson]
    # print(vjson)
    frequencies = dict(zip(Counter(vjson).keys(), Counter(vjson).values()))
    kvjson = re.compile('kvjson:(.*)').findall(output.decode('utf-8'))
    kvjson = [float(i)*1000 for i in kvjson]
    fold = [float(i)*1000
            for i in re.compile('fold:(.*)').findall(output.decode('utf-8'))]
    call_count = [int(i)
                  for i in re.compile('called:(.*)').findall(output.decode('utf-8'))]
    fold_compare = [float(i)*1000
                    for i in re.compile('fold_compare:(.*)').findall(output.decode('utf-8'))]
    # infold = [float(i)*1000
    #           for i in re.compile('in-fold:(.*)').findall(output.decode('utf-8'))]
    concat = [float(i)*1000
              for i in re.compile('concat:(.*)').findall(output.decode('utf-8'))]
    # print('In scilla runner:')
    init_res = float(re.search(b'init_res:(.*)', output)[1])*1000
    cstate = float(re.search(b'cstate:(.*)', output)[1])*1000
    step_result = float(re.search(b'step_result:(.*)', output)[1])*1000
    exec_step = float(re.search(b'exec:(.*)', output)[1])*1000
    osj = float(re.search(b'output_state_json:(.*)', output)[1])*1000
    omj = float(re.search(b'output_message_json:(.*)', output)[1])*1000
    oej = float(re.search(b'output_event_json:(.*)', output)[1])*1000
    all_time_taken = float(all_time_match[1]) * 1000
    output_state_time_taken = float(output_state_match[1]) * 1000
    all_without_osj = all_time_taken - output_state_time_taken

    # print('all time:'.ljust(8), '{0:.6} ms'.format(all_time_taken))
    # print('init_res:'.ljust(8), '{0:.6} ms'.format(init_res))
    # print('cstate:'.ljust(8), '{0:.6} ms'.format(cstate))
    # print('step_result:'.ljust(8), '{0:.6} ms'.format(step_result))
    # print('exec_step:'.ljust(8), '{0:.6} ms'.format(exec_step))
    # print('osj:'.ljust(8), '{0:.6} ms'.format(osj))
    # print('omj:'.ljust(8), '{0:.6} ms'.format(omj))
    # print('oej:'.ljust(8), '{0:.6} ms'.format(oej))

    # strlit = int(re.search(b'string:(.*)', output)[1])
    # bnumlit = int(re.search(b'bnum:(.*)', output)[1])
    # bystrlit = int(re.search(b'bystr:(.*)', output)[1])
    # bystrxlit = float(re.search(b'bystrx:(.*)', output)[1])*1000
    # intlit = int(re.search(b'int:(.*)', output)[1])
    # uintlit = float(re.search(b'uint:(.*)', output)[1])*1000
    # print('strlit:'.ljust(8), '{} times'.format(strlit))
    # print('bnumlit:'.ljust(8), '{} times'.format(bnumlit))
    # print('bystrlit:'.ljust(8), '{} times'.format(bystrlit))
    # print('bystrxlit:'.ljust(8), '{0:.6} ms'.format(bystrxlit))
    # print('intlit:'.ljust(8), '{} times'.format(intlit))
    # print('uintlit:'.ljust(8), '{0:.6} ms'.format(uintlit))

    # print()
    # print('In map:')
    # print('map:'.ljust(8), '{0:.6} ms'.format(sum(mapvalues)))
    # print('kjson:'.ljust(8), '{0:.6} ms'.format(sum(kjson)))
    # print('vjson:'.ljust(8), '{0:.6} ms'.format(sum(vjson)))
    # print('kvjson:'.ljust(8), '{0:.6} ms'.format(sum(kvjson)))
    # # # print('in-fold:'.ljust(8), '{0:.6} ms'.format(sum(infold)))
    # print('fold:'.ljust(8), '{0:.6} ms'.format(sum(fold)))
    # # print('fold_compare:'.ljust(8), '{0:.6} ms'.format(sum(fold_compare)))
    # print('concat:'.ljust(8), '{0:.6} ms'.format(sum(concat)))
    # print('called:'.ljust(8), '{} times'.format(sum(call_count)))
    return all_time_taken, output_state_time_taken, all_without_osj,\
        sum(kjson), sum(vjson), sum(fold), sum(concat), sum(kvjson)


def run_benchmark(no_of_state_entries, iterations=100):
    benchmark_plans = get_benchmark_plans(no_of_state_entries, iterations)
    for contract_plan in benchmark_plans:
        contract_name = contract_plan['contract']
        test_plans = contract_plan['tests']
        print('Using {:,} state entries...'.format(no_of_state_entries))
        create_state_file(contract_name, contract_plan['state'])

        for test_plan in test_plans:
            execution_times = []
            output_state_times = []
            percentage = []
            kjson_times = []
            vjson_times = []
            kvjson_times = []
            fold_times = []
            concat_times = []
            without_osj_times = []
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
                all_time_taken, output_state_time, all_without_osj,\
                    kjson, vjson, fold, concat, kvjson = run_test(
                        contract_name, transaction, blockchain_json=bjson)
                execution_times.append(all_time_taken)
                output_state_times.append(output_state_time)
                without_osj_times.append(all_without_osj)
                kjson_times.append(kjson)
                vjson_times.append(vjson)
                concat_times.append(concat)
                kvjson_times.append(kvjson)
                fold_times.append(fold)

            kjson_percent = [(kjson_times[i]/fold_times[i])
                             * 100 for i in range(len(kjson_times))]
            vjson_percent = [(vjson_times[i]/fold_times[i])
                             * 100 for i in range(len(vjson_times))]
            kvjson_percent = [(kvjson_times[i]/fold_times[i])
                              * 100 for i in range(len(kvjson_times))]
            concat_percent = [(concat_times[i]/fold_times[i])
                              * 100 for i in range(len(concat_times))]
            fold_percent = [(fold_times[i]/execution_times[i])
                            * 100 for i in range(len(fold_times))]

            print('Using {:,} state entries in {} contract'.format(
                no_of_state_entries, contract_name))
            print('Ran {} iterations of `{}` function'.format(
                iterations, test_name))
            # print('New database size: {:,} bytes'.format(
            #     calculate_all_db_key_value_sizes()))
            print('Median execution time: {0:.6f} ms'.format(
                median(execution_times)))
            print('Mean execution time: {0:.6f} ms'.format(
                mean(execution_times)))
            print('    Median execution without output state time: {0:.6f} ms'.format(
                median(without_osj_times)))
            print('    Median output state JSON time: {0:.6f} ms'.format(
                median(output_state_times)))
            # print('Median kjson: {0:.6f} ms'.format(
            #     median(kjson_times)))
            # print('Median vjson: {0:.6f} ms'.format(
            #     median(vjson_times)))
            print('        Median fold as %: {0:.6f}'.format(
                median(fold_percent)))
            print('            Median kjson as %: {0:.6f}'.format(
                median(kjson_percent)))
            print('            Median vjson as %: {0:.6f}'.format(
                median(vjson_percent)))
            print('            Median kvjson as %: {0:.6f}'.format(
                median(kvjson_percent)))
            print('            Median concat as %: {0:.6f}'.format(
                median(concat_percent)))
            # print('Median fold: {0:.6f} ms'.format(
            #     median(fold_times)))
            print()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        run_benchmark(int(sys.argv[1]), int(sys.argv[2]))
    else:
        run_benchmark(int(sys.argv[1]))
