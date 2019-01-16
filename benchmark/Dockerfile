FROM ubuntu:16.04

ENV PATH=/usr/lib/go-1.9/bin:$PATH

RUN \
  apt-get update && apt-get upgrade -q -y && \
  apt-get install -y --no-install-recommends golang-1.9 git make gcc libc-dev ca-certificates && \
  export GOPATH=/home/docker/go && \
  export GOROOT=/usr/lib/go-1.9 && \
  curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh && \
  mkdir -p $GOPATH/src/github.com/CoinCulture && \
  git clone https://github.com/CoinCulture/evm-tools $GOPATH/src/github.com/CoinCulture/evm-tools && \
  cd $GOPATH/src/github.com/CoinCulture/evm-tools && \
  dep ensure && \
  make && \
  apt-get remove -y golang-1.9 git make gcc libc-dev && apt autoremove -y && apt-get clean

ADD . /code/

WORKDIR /code/

ENTRYPOINT ["./build/bin/geth"]
