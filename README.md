# zilliqa-benchmarks

This repository is used to benchmark the execution performance (without IO) of Scilla against EVM.

## Installation

To run the benchmarks, you must have [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

In the root directory, run these commands:

```
docker-compose build
docker-compose up -d

# use this to get the container ID
docker ps

docker exec -it <container_id> bash

# in the container
# for unknown reasons, you cannot compile Scilla when building the container
# build it manually first...

cd /home/scilla
make

cd /code

# to run the benchmark
# python3.6 scilla-benchmark/scilla_benchmark.py <state_entries> <number_of_iterations>
python3.6 scilla-benchmark/scilla_benchmark.py 500000 10
