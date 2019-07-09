FROM ubuntu:16.04

ENV PATH=/usr/lib/go-1.9/bin:$PATH

RUN apt-get update && apt-get upgrade -q -y 

RUN apt-get install -y software-properties-common

RUN \
  add-apt-repository ppa:ethereum/ethereum && \
  add-apt-repository ppa:deadsnakes/ppa && \
  add-apt-repository ppa:tah83/secp256k1 -y && \
  add-apt-repository -y ppa:avsm/ppa && \
  apt-get update

RUN apt-get install -y --no-install-recommends git ca-certificates curl \
   g++ build-essential make gcc libc-dev \
  solc python3.6 python3.6-dev gnupg m4 ocaml \
  opam pkg-config zlib1g-dev libgmp-dev libffi-dev libssl-dev \
  libboost-system-dev libsecp256k1-dev libsqlite3-dev libpcre3-dev

RUN rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6

RUN opam init -y --disable-sandboxing

RUN opam switch create -y 4.06.1

RUN opam install -y ocaml-migrate-parsetree core cryptokit ppx_sexp_conv yojson batteries angstrom hex ppx_deriving ppx_deriving_yojson menhir oUnit dune stdint fileutils ctypes ctypes-foreign bisect_ppx secp256k1 patdiff
  
RUN echo ". ~/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true " >> ~/.bashrc

## MOVE THIS UP
RUN apt-get update && apt-get install -y wget

WORKDIR /code

ADD requirements.txt /code/
RUN pip install -r requirements.txt

## SCILLA BENCHMARK

WORKDIR /home

ADD ./scilla-benchmark/dist-scilla/scilla.zip /home

RUN unzip /home/scilla.zip

WORKDIR /home/scilla

RUN eval `opam config env` && make

WORKDIR /code/scilla-benchmark

#RUN cd /home/scilla && make

ADD ./scilla-benchmark /code/scilla-benchmark

RUN mkdir output

# ENTRYPOINT ["python3.6", "scilla_benchmark.py"]

## EVM

ENV LEVELDB_VER="1.20"

RUN \
  wget https://github.com/google/leveldb/archive/v${LEVELDB_VER}.tar.gz && \
  tar xvf v${LEVELDB_VER}.tar.gz && \
  rm -f v${LEVELDB_VER}.tar.gz && \
  cd leveldb-${LEVELDB_VER} && \
  make && \
  cp -r out-static/lib* out-shared/lib* "/usr/local/lib" && \
  cd include && \
  cp -r leveldb /usr/local/include

RUN cd leveldb-${LEVELDB_VER} && ldconfig

RUN curl -O https://storage.googleapis.com/golang/go1.9.1.linux-amd64.tar.gz
RUN tar -xvf go1.9.1.linux-amd64.tar.gz
RUN mv go /usr/local

ENV PATH=/usr/local/go/bin:$PATH

ENV GOPATH=/home/docker/go
# ENV GOROOT=/usr/lib/go-1.9
# ENV GOBIN=/usr/lib/go-1.9
ENV GOROOT=/usr/local/go
ENV GOBIN=/usr/local/go

RUN \
  curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh && \
  mkdir -p $GOPATH/src/github.com/kenchangh

ADD ./evm-benchmark/dist-evm/evm-tools.zip $GOPATH/src/github.com/kenchangh

WORKDIR $GOPATH/src/github.com/kenchangh

RUN unzip evm-tools.zip

# git clone https://github.com/kenchangh/evm-tools $GOPATH/src/github.com/kenchangh/evm-tools

WORKDIR $GOPATH/src/github.com/kenchangh/evm-tools

RUN $GOROOT/dep ensure && make

WORKDIR /code/evm-benchmark

ADD ./evm-benchmark /code/evm-benchmark
