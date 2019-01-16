FROM ubuntu:16.04

ENV PATH=/usr/lib/go-1.9/bin:$PATH

RUN \
  apt-get update && apt-get upgrade -q -y && \
  apt-get install -y --no-install-recommends golang-1.9 git make gcc libc-dev ca-certificates curl software-properties-common

RUN \
  add-apt-repository ppa:ethereum/ethereum && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get -y install solc python3.6 python3.6-dev && \
  curl https://bootstrap.pypa.io/get-pip.py | python3.6

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
