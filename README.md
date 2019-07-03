# Scilla-benchmarks

This repository contains the benchmarking suite for testing the performance of Scilla against EVM.

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

## Interpreting Scilla test results

This is an example output from the Scilla benchmark.

```
Using 10 state entries...
Running 10 iterations of `Transfer` function
Ran 0 iterations
Using 10 state entries in fungible-token contract
Ran 10 iterations of `Transfer` function
Median total time: 0.687500 ms
    Median init time: 0.541000 ms
    Median exec time: 0.067500 ms
    Median serialize time: 0.048000 ms
    Median write time: 0.028000 ms
```

Init time refers to the time taken for the JSON state file to be parsed as Ocaml JSON types.

Exec time refers to the time taken for the interpreter to execute the Scilla source code.

Serialize time refers to the time taken to convert Scilla data types into JSON data types.

Write time refers to the time taken to write the JSON files to disk after everything is done.

## Interpreting EVM test results

This is an example output from the EVM benchmark. The output is a bit verbose.

```
Using 10 state entries
Compiler run successful. Artifact(s) can be found in directory /code/output.
Compiled ERC20 to /code/output/ERC20.bin
ERC20 source size is: 6696
Running 10 iterations of `transfer` function
Encoding params 0.005234479904174805
Write bytecode to file 1.6689300537109375e-05
VM STAT 0 OPs
Deploy to EVM 0.3471808433532715
Contract deployed at: 0x8FDB05EC41FD46A4EE55A019A9D80171424890A3
Contract bytecode size: 4,214 bytes
Initial EVM database size: 3,325 bytes
Ran 10 iterations
Ran 10 iterations of transfer function
New database size: 3,584 bytes
Median execution time: 0.337750 ms
Mean execution time: 0.444220 ms
Median init time: 299.500000 ms
Median IO time: 0.000000 ms
```

First, you can see the compiled contract bytecode size in `Contract bytecode size`.

Init time refers to the time taken to create a new EVM environment and load the state database.

Execution time refers to the time taken to execute all the opcodes in the bytecode.

IO time refers to the time taken to commit the changes to the state database.

EVM does not have an equivalent of Serialize time (as in Scilla) as they do not need to serialize into JSON strings.

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
