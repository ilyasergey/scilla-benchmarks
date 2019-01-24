FROM ubuntu:16.04

ENV PATH=/usr/lib/go-1.9/bin:$PATH

RUN \
  apt-get update && apt-get upgrade -q -y && \
  apt-get install -y --no-install-recommends git ca-certificates curl software-properties-common g++ build-essential

RUN \
  add-apt-repository ppa:tah83/secp256k1 -y && \
  add-apt-repository -y ppa:avsm/ppa && \
  apt-get update && apt-get upgrade -q -y && \
  apt-get install -y --no-install-recommends curl build-essential m4 ocaml opam pkg-config zlib1g-dev libgmp-dev libffi-dev libssl-dev libboost-system-dev libsecp256k1-dev libsqlite3-dev


RUN opam init -y --disable-sandboxing

RUN opam switch create -y 4.06.1

RUN opam install -y ocaml-migrate-parsetree core cryptokit ppx_sexp_conv yojson batteries angstrom hex ppx_deriving ppx_deriving_yojson menhir oUnit dune stdint fileutils ctypes ctypes-foreign bisect_ppx secp256k1
  
RUN echo ". ~/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true " >> ~/.bashrc

RUN eval `opam config env`


RUN \
  add-apt-repository ppa:ethereum/ethereum && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get -y install solc python3.6 python3.6-dev && \
  curl https://bootstrap.pypa.io/get-pip.py | python3.6

RUN \
  git clone https://github.com/Zilliqa/scilla /home/scilla

WORKDIR /home/scilla

RUN make clean && make

WORKDIR /code/
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
