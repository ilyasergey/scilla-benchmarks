import re
import uuid
from threading import Thread
from queue import Queue
import subprocess


def run_scilla_benchmark(queue, state_size, iterations=100):
    state_size = str(state_size)
    iterations = str(iterations)
    container_id = str(uuid.uuid4())

    output = subprocess.check_output(['docker', 'run', '--name', container_id,
                                      '-it', 'scilla-benchmarks_scilla-benchmark', state_size, iterations])
    queue.put(output)


def run_breakdown():
    state_sizes = [10000, 50000, 100000]
    state_breakdown = {}
    queue = Queue()
    threads = [Thread(target=run_scilla_benchmark, args=(queue, size, 100))
               for size in state_sizes]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    outputs = tuple(queue.queue)
    results = [parse_output(output.decode('utf-8')) for output in outputs]

    for index, result in enumerate(results):
        size = state_sizes[index]
        state_breakdown[size] = result
    print(state_breakdown)


def parse_output(output):
    functions = ['ft-transfer', 'nft-setApproveForAll',
                 'auc-bid', 'cfd-pledge']

    function_times = {}
    for function in functions:
        function_times[function] = {
            'init': 0,
            'exec': 0,
            'serialize': 0,
            'write': 0
        }
    time_names = ['init', 'exec', 'serialize', 'write']

    init_times = re.finditer('Median init time: (\\d*\\.?\\d*) ms', output)
    exec_times = re.finditer('Median exec time: (\\d*\\.?\\d*) ms', output)
    serialize_times = re.finditer(
        'Median serialize time: (\\d*\\.?\\d*) ms', output)
    write_times = re.finditer('Median write time: (\\d*\\.?\\d*) ms', output)
    all_times = [init_times, exec_times, serialize_times, write_times]

    for time_index, times in enumerate(all_times):
        for function_index, time_match in enumerate(times):
            time_name = time_names[time_index]
            function_name = functions[function_index]
            function_times[function_name][time_name] = float(time_match[1])
    return function_times


if __name__ == '__main__':
    run_breakdown()
