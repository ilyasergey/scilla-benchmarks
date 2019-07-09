import os
import sys
import re
import uuid
from threading import Thread
from queue import Queue
import subprocess
from charts import plot_relative_time, plot_comparison_bar_chart,\
    plot_compare_sizes
from common import STATE_SIZES, TIME_NAMES, FUNCTION_NAMES,\
    COMPARISON_STATE_SIZES, INTERPRETERS, CONTRACTS, CONTRACT_SIZE_NAMES,\
    READABLE_INTERPRETER_NAMES

root_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(root_dir, 'results')


def run_benchmark(queue, interpreter, state_size, iterations):
    script_file = '{interpreter}-benchmark/{interpreter}_benchmark.py'.format(
        interpreter=interpreter)

    output = subprocess.check_output(
        ['python3.6', script_file, str(state_size), str(iterations)],
        stderr=subprocess.DEVNULL)

    # output = subprocess.check_output(['docker', 'run', '--name', container_id,
    #                                   '-it', image_name, str(state_size), str(iterations)])
    queue.put((interpreter, state_size, output))

    # # make the terminal less janky
    # subprocess.call(['stty', 'sane'])

    # subprocess.call(['docker', 'rm', container_id], stdout=subprocess.DEVNULL)

    print('Completed {} benchmark for state size of {:,} with {} iterations'.format(
        interpreter, state_size, iterations))


def run_scilla_vs_evm_exec():
    queue = Queue()
    interpreter_times = {}
    print('Running benchmarks on size 10k, 50k')

    for interpreter in INTERPRETERS:
        interpreter_times[interpreter] = {}

        for size in COMPARISON_STATE_SIZES:
            run_benchmark(queue, interpreter, size, 5)

    outputs = tuple(queue.queue)
    for parse_output in outputs:
        interpreter, size, output = parse_output
        times = parse_exec_times(interpreter, output.decode('utf-8'))
        interpreter_times[interpreter][size] = times

    plot_data = transform_to_comparison_data(interpreter_times)

    print_exec_table(plot_data)

    filename = 'scilla-evm-execution-time.png'
    filepath = os.path.join(results_dir, filename)
    plot_comparison_bar_chart(plot_data, filepath)

    print('\nSaved the chart to {}'.format(filepath))


def run_size_comparison():
    queue = Queue()
    interpreter_sizes = {}
    print('Reading code sizes...')

    for interpreter in INTERPRETERS:
        run_benchmark(queue, interpreter, 1, 1)

    outputs = tuple(queue.queue)

    for parse_output in outputs:
        interpreter, _, output = parse_output

        if interpreter == 'scilla':
            sizes = parse_contract_size(interpreter, output)
            interpreter_sizes[interpreter] = sizes
        elif interpreter == 'evm':
            sol_sizes = parse_contract_size('evm-sol', output)
            bytecode_sizes = parse_contract_size('evm-bytecode', output)
            interpreter_sizes['evm-sol'] = sol_sizes
            interpreter_sizes['evm-bytecode'] = bytecode_sizes

    plot_data = transform_to_compare_size(interpreter_sizes)
    print_size_table(plot_data)

    filename = 'code-size-comparison.png'
    filepath = os.path.join(results_dir, filename)
    plot_compare_sizes(plot_data, filepath)

    print('\nSaved the chart to {}'.format(filepath))


def print_exec_table(data):
    contracts_10k = [contract+'-10' for contract in CONTRACTS]
    contracts_50k = [contract+'-50' for contract in CONTRACTS]
    all_contracts = contracts_10k + contracts_50k
    separator = ' | '

    print('\nRESULTS (in milliseconds):\n')

    header_row = ' ' * 8 + separator

    for contract_name in all_contracts:
        header_row += '{:>12}'.format(contract_name)
        header_row += separator
    print(header_row)

    divider_row = '-' * 8 + ' + '

    for _ in all_contracts:
        divider_row += '-' * 12 + ' + '
    print(divider_row)

    for index, interpreter in enumerate(INTERPRETERS):
        readable_interpreter_name = READABLE_INTERPRETER_NAMES[interpreter]
        row = '{:<8}'.format(readable_interpreter_name) + separator
        interpreter_data = data[index]

        for time in interpreter_data:
            row += '{:>12.2f}'.format(time)
            row += separator
        print(row)

    print()


def print_size_table(data):
    separator = ' | '

    print('\nNote: Code sizes will not change in size, as the programs are written beforehand.')
    print('They can be inspected in scilla-benchmark/contracts and evm-benchmark/contracts.')

    print('\nRESULTS (in bytes):\n')

    header_row = ' ' * 15 + separator

    for contract_name in CONTRACTS:
        header_row += '{:>12}'.format(contract_name)
        header_row += separator
    print(header_row)

    divider_row = '-' * 15 + ' + '

    for _ in CONTRACTS:
        divider_row += '-' * 12 + ' + '
    print(divider_row)

    for index, interpreter in enumerate(CONTRACT_SIZE_NAMES):
        readable_interpreter_name = READABLE_INTERPRETER_NAMES[interpreter]
        row = '{:<15}'.format(readable_interpreter_name) + separator
        interpreter_data = data[index]

        for time in interpreter_data:
            row += '{:>12}'.format(time)
            row += separator
        print(row)

    print()


def parse_contract_size(interpreter, output):
    re_pattern = None
    if interpreter == 'scilla':
        re_pattern = 'Contract size: (\\d*) bytes'
    elif interpreter == 'evm-sol':
        re_pattern = 'source size is: (\\d*)'
    elif interpreter == 'evm-bytecode':
        re_pattern = 'Contract bytecode size: (\\d*) bytes'

    matches = re.finditer(re_pattern, output.decode('utf-8'))
    sizes = {}

    for index, match in enumerate(matches):
        contract_name = CONTRACTS[index]
        size = int(match[1])
        sizes[contract_name] = size
    return sizes


def transform_to_compare_size(data):
    plot_data = []

    for interpreter in CONTRACT_SIZE_NAMES:
        size_data = []

        for contract_name in CONTRACTS:
            size_data.append(data[interpreter][contract_name])
        plot_data.append(size_data)
    return plot_data


def parse_exec_times(interpreter, output):
    re_pattern = None
    if interpreter == 'scilla':
        re_pattern = 'Median total time: (\\d*\\.?\\d*) ms'
    elif interpreter == 'evm':
        re_pattern = 'Median total time: (\\d*\\.?\\d*) ms'

    exec_times = re.finditer(re_pattern, output)
    times = {}

    for index, time_match in enumerate(exec_times):
        function_name = FUNCTION_NAMES[index]
        times[function_name] = float(time_match[1])
    return times


def transform_to_comparison_data(data):
    plot_data = []

    for interpreter in INTERPRETERS:
        time_data = []

        for size in COMPARISON_STATE_SIZES:
            for function_name in FUNCTION_NAMES:
                time_data.append(data[interpreter][size][function_name])
        plot_data.append(time_data)
    return plot_data


def run_breakdown():
    state_breakdown = {}
    queue = Queue()

    for size in STATE_SIZES:
        run_benchmark(queue, 'scilla', size, 1)

    print('Running benchmarks on size 10k, 100k, 500k')

    outputs = tuple(queue.queue)
    results = [parse_output(output.decode('utf-8'))
               for interpreter, state_size, output in outputs]

    for index, result in enumerate(results):
        size = STATE_SIZES[index]
        state_breakdown[size] = result

    print('\nRESULTS (in milliseconds):')
    table_data = transform_to_table_data(state_breakdown)
    print_table_data(table_data)
    print()

    plot_data = transform_to_plot_data(state_breakdown)

    filename = 'relative-time-breakdown.png'
    filepath = os.path.join(results_dir, filename)
    plot_relative_time(plot_data, filepath)

    print('\nSaved the chart to {}'.format(filepath))


def parse_output(output):
    function_times = {}
    for function in FUNCTION_NAMES:
        function_times[function] = {
            'init': 0,
            'exec': 0,
            'serialize': 0,
            'write': 0
        }

    init_times = re.finditer('Median init time: (\\d*\\.?\\d*) ms', output)
    exec_times = re.finditer('Median exec time: (\\d*\\.?\\d*) ms', output)
    serialize_times = re.finditer(
        'Median serialize time: (\\d*\\.?\\d*) ms', output)
    write_times = re.finditer('Median write time: (\\d*\\.?\\d*) ms', output)
    all_times = [init_times, exec_times, serialize_times, write_times]

    for time_index, times in enumerate(all_times):
        for function_index, time_match in enumerate(times):
            time_name = TIME_NAMES[time_index]
            function_name = FUNCTION_NAMES[function_index]
            function_times[function_name][time_name] = float(time_match[1])
    return function_times


def transform_to_plot_data(data):
    plot_data = []

    for size in STATE_SIZES:
        time_data = []

        for time in TIME_NAMES:
            function_data = []

            for function_name in FUNCTION_NAMES:
                function_data.append(data[size][function_name][time])

            time_data.append(function_data)
        plot_data.append(time_data)

    return plot_data


def transform_to_table_data(data):
    table_data = []

    for function_name in FUNCTION_NAMES:
        time_data = []

        for time in TIME_NAMES:
            size_data = []

            for size in STATE_SIZES:
                size_data.append(data[size][function_name][time])
            time_data.append(size_data)
        table_data.append(time_data)

    return table_data


def print_table_data(table_data):
    left_margin = 22
    data_left_padding = 10
    group_separator = ' | '

    upper_header_row = ' ' * left_margin + group_separator

    for time_name in TIME_NAMES:
        upper_header_row += ('{:^'+str(data_left_padding*3) +
                             's}').format(time_name)
        upper_header_row += group_separator
    print(upper_header_row)

    upper_header_div = ' ' * left_margin + group_separator

    for _ in range(len(TIME_NAMES)):
        upper_header_div += '-' * (data_left_padding * 3)
        upper_header_div += ' + '
    print(upper_header_div)

    lower_header_row = (
        '{:<'+str(left_margin)+'}').format('Transition/State size')
    lower_header_row += group_separator

    for _ in range(len(TIME_NAMES)):
        for size in STATE_SIZES:
            size_header = str(size//1000)+'k'
            lower_header_row += ('{:>'+str(data_left_padding) +
                                 '}').format(size_header)
        lower_header_row += group_separator
    print(lower_header_row)

    for function_index, function_data in enumerate(table_data):
        function_name = FUNCTION_NAMES[function_index]
        row_str = ('{:<'+str(left_margin)+'}').format(function_name)
        row_str += group_separator

        for time_data in function_data:
            for time in time_data:
                row_str += ('{:>'+str(data_left_padding) +
                            '.2f}').format(time)
            row_str += group_separator
        print(row_str)


def create_results_dir():
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)


if __name__ == '__main__':
    no_cmd = 'available commands are breakdown, exec, size'

    if len(sys.argv) < 2:
        print('No command specified. ' + no_cmd)
        sys.exit()

    command = sys.argv[1]

    create_results_dir()

    if command == 'breakdown':
        run_breakdown()
    elif command == 'exec':
        run_scilla_vs_evm_exec()
    elif command == 'size':
        run_size_comparison()
    else:
        print("No commmand '{}' found".format(command) + '. ' + no_cmd)
