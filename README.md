# zilliqa-benchmarks

This repository is used to benchmark the execution performance (without IO) of Scilla against EVM.

## Installation

To run the benchmarks, you must have [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

In the root directory, run the `build` command to build the images:

```
docker-compose build
```

Next, you can start running the benchmarks for either Scilla or EVM. The parameters are stated below.

```
# to run the benchmark
# docker run -it zilliqa-benchmarks_<interpreter>-benchmark <number_of_state_entries> <test_iterations>

# for Scilla
docker run -it zilliqa-benchmarks_scilla-benchmark 10000 10

# for EVM
docker run -it zilliqa-benchmarks_evm-benchmark 10000 10
```

## Choosing tests

Currently, choosing which contracts and tests to run is manual. The benchmarking suite defaults to running all contracts and all functions. You may uncomment the files in `evm-benchmark/benchmark_plans.py` and `scilla-benchmark/benchmark_plans.py`.

Below is an example contract being tested. If you want to remove the contract from the benchmark, you can comment it out completely. Or, you can comment out the individual tests of the functions in the `tests` property.

```
{
            'contract': 'fungible-token',
            'state':  [
                ....
            ],
            'tests': [
                {
                    'test_name': 'Transfer',
                    'transactions': [
                        {
                            'transition': 'Transfer',
                            'amount': '0',
                            'sender': SENDER_ADDRESS,
                            'params': [
                                {
                                    'vname': 'to',
                                    'type': 'ByStr20',
                                    'value': '0x44345678901234567890123456789012345678cd'
                                },
                                {
                                    'vname': 'tokens',
                                    'type': 'Uint128',
                                    'value': '1000'
                                },
                            ],
                        }
                        for addr in addresses[
                            state_entries:state_entries+test_iterations]
                    ]
                }
            ]
        },
```
