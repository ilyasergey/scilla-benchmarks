# Scilla Benchmarks

This is the artefact accompanying the OOPSLA 2019 paper entitled _"Safer Smart Contract Programming with Scilla"_. The artefact contains scripts for reproducing the quantitative comparison with Ethereum Virtual Machine, reported in Section 6.2 of the paper.

This repository contains the benchmarking suite for testing the performance of Scilla against EVM.

## Prerequisites

In order to run the benchmarks, you must have the [Docker](https://www.docker.com) platform installed and the docker daemon running.

The source of this artefact can be obtained from GitHub:
```
git clone https://github.com/ilyasergey/scilla-benchmarks
```

## Installation

Once you have the Docker daemon running, in the root directory of `scilla-benchmarks` build the image with the command:

```
docker build -t scilla-benchmarks:oopsla scilla-benchmarks
```

This will take a while as it downloads all the project's dependencies and compiles OCaml libraries.
In particular, it's expected that the build process doesn't produce output for several minutes when you see the following text on the screen

```shell
<><> Gathering sources ><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
[ocaml-base-compiler.4.06.1] downloaded from cache at https://opam.ocaml.org/cache

<><> Processing actions <><><><><><><><><><><><><><><><><><><><><><><><><><><><>
```

## Reproducing the Results

To produce the benchmark results, a Docker container is used to run the tests.

The docker container takes in `command` to run, where `command` could be `breakdown`, `exec`, `size`, `unit-test` or `single-test`.

In the prior rounds of testing when the paper was written, the number of test iterations used was 100. However, due to the long time it takes to complete a test, for example when 500k state entries are used, the test iterations are lowered. They are set to 5 iterations for the `exec` command and 1 iteration for the `breakdown` command.

The results may be slightly different from what was written in the paper, due to the lack of averaging.

```shell
docker run -it scilla-benchmarks:oopsla <command>
```

After every time the command is run, to retrieve the output from the container, run

```shell
docker cp $(docker ps -alq):/code/results .
```

This copies generated chart images into the `./results` directory.

---

### Relative time breakdown

The `breakdown` command generates the relative time breakdown of execution of Scilla smart contracts. This breaks down a Scilla contract execution into multiple phases, `init`, `exec`, `serialize` and `write`.

The contract transitions tested were `ft-transfer` (Fungible Token transfer), `nft-setApprovalForAll` (Non Fungible Token setApprovalForAll), `auc-bid` (Auction bid), `cfd-pledge` (Crowdfunding pledge).

The table generated reflects Table 3 (breakdown of contract run-times) and the bar chart reflects the Figure 11(a) in the paper.

```shell
docker run -it scilla-benchmarks:oopsla breakdown
```

---

### Scilla/EVM Execution time

The `exec` command generates the execution time of Scilla and EVM on (excluding phases like `init`, `serialize` and `write`).

The 4 contract transitions,`ft-transfer`, `nft-setApprovalForAll`, `auc-bid`, `cfd-pledge`, were tested with 10k and 50k state entries.

The bar chart generated reflects the Figure 11(b) of the comparison between Scilla/EVM execution times.

```shell
docker run -it scilla-benchmarks:oopsla exec
```

---

### Code size comparison

The `size` command generates the code size comparison between Scilla, Solidity and EVM bytecode. The 4 major contracts `FungibleToken`, `NonFungibleToken`, `Auction` and `Crowdfunding` were used to measure the code size. These contracts were written both in Scilla and Solidity.

_Note: The code sizes will not differ between separate runs, as pre-written code is read from disk._

They are available in `scilla-benchmarks/scilla-benchmark/contracts` and `evm-benchmarks/evm-benchmark/contracts` respectively for inspection.

The bar chart generated reflects the Figure 11(c) of the code size comparison.

```shell
docker run -it scilla-benchmarks:oopsla size
```

---

### Running unit tests

The Scilla codebase comes along with unit tests. The `unit-test` command runs these unit tests written in OCaml.

```shell
docker run -it scilla-benchmarks:oopsla unit-test
```

NOTE: The unit tests will fail with 3 failures, this is the expected behaviour. This is because the Scilla snapshot used contains instrumentation code, which affects the diff test.

---

### Running a single test

The `single-test` command runs a single test from a contract's transition. The command accepts 2 arguments, `contract_name` and `no_of_state_entries`. Below is how the command is run:

```shell
docker run -it scilla-benchmarks:oopsla single-test <contract_name> <no_of_state_entries>
```

The options for the `contract_name` are `fungible-token`, `nonfungible-token`, `auction` and `crowdfunding`.

For the `no_of_state_entries`, any integer is accepted. However, the recommendation is to use integers between `10000` to `500000`, as they reflect the paper's numbers.

For example, to run the fungible-token contract with 10k entries:

```shell
docker run -it scilla-benchmarks:oopsla single-test fungible-token 10000
```

## Submission-specific Snapshots of Scilla & EVM

The scilla infrastructure is currently under active ongoing
development. The results reported in the OOPSLA'19 submission were
compiled using the dedicated branch of the repository, containing the
snapshot as of the time of the submission, instrumented with
additional output for the sake of performance comparison with EVM.
This snapshot is available at:

[https://github.com/Zilliqa/scilla/tree/oopsla19-docker](https://github.com/Zilliqa/scilla/tree/oopsla19-docker)

Specifically, the commit hash for the Scilla distribution used is:

[https://github.com/Zilliqa/scilla/tree/0e38aae67670aeba23a7a3d6067d29ea7ca331c5](https://github.com/Zilliqa/scilla/tree/0e38aae67670aeba23a7a3d6067d29ea7ca331c5)

A packaged snapshot of Scilla source code is already prepared in the Evaluation Scripts in `scilla-benchmarks/scilla-benchmark/dist-scilla`.

Next, the `evm-tools` infrastructure is a collection of tools used to work with the EVM.
These tools have been modified to support persistence. The EVM instance is also
instrumented with additional printing for the sake of performance comparison
with Scilla. The Go-Ethereum version used by evm-tools is 1.4.10. The snapshot is available at:

[https://github.com/kenchangh/evm-tools/tree/e2324a0c362acd930a66e62382c9f0a23af38d39](https://github.com/kenchangh/evm-tools/tree/e2324a0c362acd930a66e62382c9f0a23af38d39)

A packaged snapshot of `evm-tools` is already prepared in the Evaluation Scripts in `scilla-benchmarks/evm-benchmark/dist-evm`.

## Cleaning up

In order to remove the image downloaded, run the following command:

```shell
docker rmi -f scilla-benchmarks:oopsla
```

## Elements of Scilla Implementation

This part of the artefact demonstrates the correspondence between the semantics of Scilla, presented in Figure 5 and
Figure 6 of the paper. 

Below, we refer to specific files, available immediately in the main Scilla repository, but the same files can be found in an archived Scilla snapshot, under the `scilla-benchmarks/scilla-benchmark/dist-scilla` folder of the artefact.

### Execution of Expressions and Statements. 

The following elements of the implementation correspond to the monadic pseudo-code in Figure 5:
* [Expressions](https://github.com/Zilliqa/scilla/blob/oopsla19-docker/src/lang/eval/Eval.ml#L88)
* [Statements](https://github.com/Zilliqa/scilla/blob/oopsla19-docker/src/lang/eval/Eval.ml#L242)

### The Life Cycle of a Contract. 

The following functions correspond to initialising the contract and handling the incoming messages reported in Figure 6:

* [Initialise a contract](https://github.com/Zilliqa/scilla/blob/oopsla19-docker/src/lang/eval/Eval.ml#L410)
* [Handle a message](https://github.com/Zilliqa/scilla/blob/oopsla19-docker/src/lang/eval/Eval.ml#L563)
