FROM ubuntu:16.04

ENV PATH=/usr/lib/go-1.9/bin:$PATH

RUN \
  apt-get update && apt-get upgrade -q -y && \
  apt-get install -y --no-install-recommends golang-1.9 git make gcc libc-dev ca-certificates curl software-properties-common g++ build-essential

RUN \
  add-apt-repository ppa:ethereum/ethereum && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get -y install solc python3.6 python3.6-dev && \
  curl https://bootstrap.pypa.io/get-pip.py | python3.6

RUN \
  apt-get -y install libsnappy-dev wget

ENV LEVELDB_VER="1.20"

RUN \
  wget https://github.com/google/leveldb/archive/v${LEVELDB_VER}.tar.gz && \
  tar xvf v${LEVELDB_VER}.tar.gz && \
  rm -f v${LEVELDB_VER}.tar.gz && \
  cd leveldb-${LEVELDB_VER} && \
  make && \
  cp -r out-static/lib* out-shared/lib* "/usr/local/lib" && \
  cd include && \
  cp -r leveldb /usr/local/include && \
  ldconfig


ENV GOPATH=/home/docker/go
ENV GOROOT=/usr/lib/go-1.9
ENV GOBIN=/usr/lib/go-1.9

RUN \
  curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh && \
  mkdir -p $GOPATH/src/github.com/CoinCulture && \
  git clone https://github.com/CoinCulture/evm-tools $GOPATH/src/github.com/CoinCulture/evm-tools


WORKDIR $GOPATH/src/github.com/CoinCulture/evm-tools

RUN $GOROOT/dep ensure && make

WORKDIR /code/
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
