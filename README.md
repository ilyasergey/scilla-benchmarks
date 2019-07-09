# Scilla Benchmarks

This repository contains the benchmarking suite for testing the performance of Scilla against EVM.

## Installation

### Installation from pre-built Docker image

In order to run the benchmarks, you must have the [Docker](https://www.docker.com) platform installed and the docker daemon running.

- Download the compressed (gzip) Docker image from the following Google Drive link: [scilla-benchmarks.tar.gz](https://drive.google.com/open?id=1JRYASzDVOaiN8dO6s42fya3rnxDX67Ji).
The file size is approximately 2 GB.

- Uncompress the downloaded file, but do _not_ unpack the contained `scilla-benchmarks.tar` file.
Note: macOS may automatically unzip archives after downloading them -- in this case this step may be safely skipped.
```shell
gzip -d scilla-benchmarks.tar.gz
```
The `tar`-archive file size is approximately 5 GB.

- Import the `tar`-archive as a Docker image:
```shell
docker load -i scilla-benchmarks.tar
```
This step might take a while and produce the following as the last line of the output:
```shell
Loaded image: kenchangh/scilla-benchmarks:oopsla
```

### Installation via building Docker image using recipies provided in current repository

Please skip this step if you have followed the instructions in the previous section.

In the project root directory, run the following command to build the images.

```shell
docker build -t kenchangh/scilla-benchmarks:oopsla scilla-benchmarks
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

The docker container takes in `command` to run, where `command` could be `breakdown`, `exec` or `size`.

In the prior rounds of testing when the paper was written, the number of test iterations used was 100. However, due to the long time it takes to complete a test, for example when 500k state entries are used, the test iterations are lowered. They are set to 5 iterations for the `exec` command and 1 iteration for the `breakdown` command.

The results may be slightly different from what was written in the paper, due to the lack of averaging.

```shell
docker run -it kenchangh/scilla-benchmarks:oopsla <command>
```

After every time the command is run, to retrieve the output from the container, run

```shell
docker cp $(docker ps -alq):/code/results .
```

This copies generated chart images into the results directory.

---

### Relative time breakdown

The `breakdown` command generates the relative time breakdown of execution of Scilla smart contracts. This breaks down a Scilla contract execution into multiple phases, `init`, `exec`, `serialize` and `write`.

The contract transitions tested were `ft-transfer` (Fungible Token transfer), `nft-setApprovalForAll` (Non Fungible Token setApprovalForAll), `auc-bid` (Auction bid), `cfd-pledge` (Crowdfunding pledge).

The table generated reflects Table 3 (breakdown of contract run-times) and the bar chart reflects the Figure 11(a) in the paper.

```shell
docker run -it kenchangh/scilla-benchmarks:oopsla breakdown
```

---

### Scilla/EVM Execution time

The `exec` command generates the execution time of Scilla and EVM on (excluding phases like `init`, `serialize` and `write`).

The 4 contract transitions,`ft-transfer`, `nft-setApprovalForAll`, `auc-bid`, `cfd-pledge`, were tested with 10k and 50k state entries.

The bar chart generated reflects the Figure 11(b) of the comparison between Scilla/EVM execution times.

```shell
docker run -it kenchangh/scilla-benchmarks:oopsla exec
```

---

### Code size comparison

The `size` command generates the code size comparison between Scilla, Solidity and EVM bytecode. The 4 major contracts `FungibleToken`, `NonFungibleToken`, `Auction` and `Crowdfunding` were used to measure the code size. These contracts were written both in Scilla and Solidity.

The bar chart generated reflects the Figure 11(c) of the code size comparison.

```shell
docker run -it kenchangh/scilla-benchmarks:oopsla size
```
