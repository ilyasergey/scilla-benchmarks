import re
import uuid
from threading import Thread
from queue import Queue
import subprocess
from charts import plot_comparison_bar_chart
from common import STATE_SIZES, TIME_NAMES, FUNCTION_NAMES


def run_scilla_benchmark(queue, state_size, iterations):
    state_size = str(state_size)
    iterations = str(iterations)
    container_id = str(uuid.uuid4())

    output = subprocess.check_output(['docker', 'run', '--name', container_id,
                                      '-it', 'scilla-benchmarks_scilla-benchmark', state_size, iterations])
    queue.put(output)

    # make the terminal less janky
    subprocess.call(['stty', 'sane'])

    print('Completed benchmark for state size of {:,} with {} iterations'.format(
        int(state_size), iterations))


def run_breakdown():
    state_breakdown = {}
    queue = Queue()
    threads = [Thread(target=run_scilla_benchmark, args=(queue, size, 1))
               for size in STATE_SIZES]

    for thread in threads:
        thread.start()

    print('Running benchmarks on size 10k, 100k, 500k')

    for thread in threads:
        thread.join()

    outputs = tuple(queue.queue)
    results = [parse_output(output.decode('utf-8')) for output in outputs]

    for index, result in enumerate(results):
        size = STATE_SIZES[index]
        state_breakdown[size] = result

    plot_data = transform_to_plot_data(state_breakdown)
    plot_comparison_bar_chart(plot_data)


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


if __name__ == '__main__':
    # plot_data = transform_to_plot_data()
    # plot_comparison_bar_chart(plot_data)
    run_breakdown()
