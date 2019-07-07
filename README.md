# Scilla Benchmarks

This repository contains the benchmarking suite for testing the performance of Scilla against EVM.

## Installation

In order to run the benchmarks, you must have the software listed below.

1. Docker
2. Docker Compose
3. Python3
4. Python PIP
5. Virtualenv (Optional)

It is suggested to use `pip install docker-compose` to install `docker-compose`.

In the root directory, run the `build` command to build the images:

```
docker-compose build
```

Next, you will have to install the Python dependencies with `pip`. In the root directory,

```
pip install -r requirements.txt
```

Optionally, you could use `virtualenv` to create a virtual Python environment to install the Python dependencies.

```
# create the virtualenv
virtualenv -p python3 venv

# activate the virtualenv
source venv/bin/activate

# install with venv's pip
pip install -r requirements.txt
```

## Reproducing the Results

To produce the benchmark results, a Python script is used to create Docker containers, run tests and parse the test results. The script file is `results.py`.

The script file is executed as below, where `command` could be `breakdown`, `exec` or `size`.

In the prior rounds of testing when the paper was written, the number of test iterations used was 100. However, due to the long time it takes to complete a test, for example when 500k state entries are used, the test iterations are lowered. They are set to 5 iterations for the `exec` command and 1 iteration for the `breakdown` command.

The results may be slightly different from what was written in the paper, due to the lack of averaging.

```
python3 results.py <command>
```

---

### Relative time breakdown

The `breakdown` command generates the relative time breakdown of execution of Scilla smart contracts. This breaks down a Scilla contract execution into multiple phases, `init`, `exec`, `serialize` and `write`.

The contract transitions tested were `ft-transfer` (Fungible Token transfer), `nft-setApprovalForAll` (Non Fungible Token setApprovalForAll), `auc-bid` (Auction bid), `cfd-pledge` (Crowdfunding pledge).

The table generated reflects Table 3 (breakdown of contract run-times) and the bar chart reflects the Figure 11(a) in the paper.

```
python3 results.py breakdown
```

---

### Scilla/EVM Execution time

The `exec` command generates the execution time of Scilla and EVM on (excluding phases like `init`, `serialize` and `write`).

The 4 contract transitions,`ft-transfer`, `nft-setApprovalForAll`, `auc-bid`, `cfd-pledge`, were tested with 10k and 50k state entries.

The bar chart generated reflects the Figure 11(b) of the comparison between Scilla/EVM execution times.

```
python3 results.py exec
```

---

### Code size comparison

The `size` command generates the code size comparison between Scilla, Solidity and EVM bytecode. The 4 major contracts `FungibleToken`, `NonFungibleToken`, `Auction` and `Crowdfunding` were used to measure the code size. These contracts were written both in Scilla and Solidity.

The bar chart generated reflects the Figure 11(c) of the code size comparison.

```
python3 results.py size
```
