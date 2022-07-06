FROM alpine:3.16.0 AS ss-libev
ENV SS_LIBEV="3.3.5"
RUN \
  # Source code downloads and dependent installations
  apk add asciidoc build-base c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev xmlto && \
  wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v$SS_LIBEV/shadowsocks-libev-$SS_LIBEV.tar.gz && \
  wget https://www.openssl.org/source/old/1.0.2/openssl-1.0.2u.tar.gz && \
  ls ./*.tar.gz | xargs -n1 tar xf && \
  mkdir -p /tmp/release/ && \
  \
  # Compile shadowsocks-libev
  cd ./shadowsocks-libev-$SS_LIBEV/ && \
  ./configure --prefix=/usr && make && make install && \
  mv /usr/bin/ss-local /tmp/release/ss-libev-local && \
  mv /usr/bin/ss-server /tmp/release/ss-libev-server && \
  \
  # Compile and install openssl (version 1.0.2u)
  cd ../openssl-1.0.2u/ && \
  ./config --shared --prefix=/usr && make && make install && \
  cp /usr/lib/libcrypto.so.1.0.0 /tmp/release/

FROM rust:1.62.0-alpine3.16 AS ss-rust
ENV SS_RUST="v1.15.0-alpha.5"
RUN \
  apk add git build-base && \
  mkdir -p /tmp/release/ && \
  git clone https://github.com/shadowsocks/shadowsocks-rust.git && \
  cd ./shadowsocks-rust/ && git checkout $SS_RUST && \
  cargo build --release --features "stream-cipher aead-cipher-extra aead-cipher-2022 aead-cipher-2022-extra" && \
  mv ./target/release/sslocal /tmp/release/ss-rust-local && \
  mv ./target/release/ssserver /tmp/release/ss-rust-server

FROM python:3.10.5-alpine3.16 AS ss-python
ENV SS_PYTHON_LEGACY="2.6.2"
RUN \
  apk add build-base cmake git glib-dev && \
  git clone https://github.com/dnomd343/shadowsocksr.git && \
  git clone https://github.com/shadowsocks/shadowsocks.git && \
  git clone https://github.com/dnomd343/shadowsocks-bootstrap.git && \
  wget https://github.com/shadowsocks/shadowsocks/archive/refs/tags/$SS_PYTHON_LEGACY.tar.gz && \
  mkdir -p /tmp/release/ && \
  tar xf ./*.tar.gz && \
  \
  # Package shadowsocksr
  cd ./shadowsocksr/ && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/ordereddict.py && \
  sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
  sed -i "/for path in paths:/a\        if 'libcrypto.so' in path:" ./shadowsocks/crypto/util.py && \
  sed -i "/libcrypto.so/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py && \
  python3 setup.py build && cd ./build/ && mv ./lib/ ./ssr-python/ && \
  mv ./ssr-python/shadowsocks/local.py ./ssr-python/shadowsocks/server.py ./ssr-python/ && \
  chmod +x ./ssr-python/local.py ./ssr-python/server.py && \
  BZIP2=-9 tar cjf /tmp/release/ssr-python.tar.bz2 ./ssr-python/ && \
  \
  # Package shadowsocks-python (latest version)
  cd ../../shadowsocks/ && git checkout master && \
  sed -i 's/if addr is/if addr ==/g' ./shadowsocks/common.py && \
  sed -i 's/and ip is not/and ip !=/g' ./shadowsocks/common.py && \
  sed -i 's/if len(block) is/if len(block) ==/g' ./shadowsocks/common.py && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
  python3 setup.py build && cd ./build/ && mv ./lib/ ./ss-python/ && \
  mv ./ss-python/shadowsocks/local.py ./ss-python/shadowsocks/server.py ./ss-python/ && \
  chmod +x ./ss-python/local.py ./ss-python/server.py && \
  BZIP2=-9 tar cjf /tmp/release/ss-python.tar.bz2 ./ss-python/ && \
  \
  # Package shadowsocks-python (legacy version)
  cd ../../shadowsocks-$SS_PYTHON_LEGACY/ && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
  sed -i "s/find_library(p)/'libsodium.so.23'/g" ./shadowsocks/crypto/ctypes_libsodium.py && \
  sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
  python3 setup.py build && cd ./build/ && mv ./lib/ ./ss-python-legacy/ && \
  mv ./ss-python-legacy/shadowsocks/local.py ./ss-python-legacy/shadowsocks/server.py ./ss-python-legacy/ && \
  chmod +x ./ss-python-legacy/local.py ./ss-python-legacy/server.py && \
  BZIP2=-9 tar cjf /tmp/release/ss-python-legacy.tar.bz2 ./ss-python-legacy/ && \
  \
  # Compile shadowsocks-bootstrap
  cd ../../shadowsocks-bootstrap/ && mkdir ./build/ && \
  cd ./build/ && cmake -DCMAKE_BUILD_TYPE=Release .. && make && \
  mv ../bin/* /tmp/release/ && \
  \
  # Build numpy and salsa20 python module
  mkdir /tmp/salsa20/ && \
  pip3 install numpy salsa20 && \
  cd /usr/local/lib/python*/site-packages/ && \
  mv ./*numpy* ./*salsa20* /tmp/salsa20/ && \
  cd /tmp/salsa20/ && rm -rf `find ./ -name '__pycache__'` && \
  BZIP2=-9 tar cjf /tmp/release/salsa20.tar.bz2 ./*

FROM rust:1.62.0-alpine3.16 AS plugin-1
RUN \
  apk add asciidoc autoconf automake build-base git libev-dev libtool linux-headers xmlto && \
  git clone https://github.com/shadowsocks/qtun.git && \
  git clone https://github.com/shadowsocks/simple-obfs.git && \
  mkdir /tmp/release/ && \
  # Compile simple-obfs
  cd ./simple-obfs/ && \
  git submodule update --init --recursive && \
  ./autogen.sh && ./configure && make && make install && \
  mv /usr/local/bin/obfs-local /usr/local/bin/obfs-server /tmp/release/ && \
  \
  # Compile qtun
  cd ../qtun/ && \
  cargo build --release && \
  mv ./target/release/qtun-client /tmp/release/ && \
  mv ./target/release/qtun-server /tmp/release/

FROM golang:1.16.15-alpine3.15 AS plugin-2
ENV GOST_PLUGIN="v1.6.3"
RUN \
  apk add git && mkdir /tmp/release/ && \
  git clone https://github.com/Qv2ray/gun.git && \
  git clone https://github.com/dnomd343/kcptun.git && \
  git clone https://github.com/dnomd343/GoQuiet.git && \
  git clone https://github.com/ihciah/rabbit-tcp.git && \
  git clone https://github.com/dnomd343/rabbit-plugin.git && \
  git clone https://github.com/maskedeken/gost-plugin.git && \
  git clone https://github.com/shadowsocks/v2ray-plugin.git && \
  git clone https://github.com/IrineSistiana/mos-tls-tunnel.git && \
  \
  # Compile v2ray-plugin
  cd ./v2ray-plugin/ && VERSION=`git describe --tags` && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" && \
  mv ./v2ray-plugin /tmp/release/ && \
  \
  # Compile kcptun
  cd ../kcptun/ && git checkout sip003 && VERSION=`git describe --tags` && \
  go mod init github.com/shadowsocks/kcptun && go mod tidy && \
  env CGO_ENABLED=0 go build -o kcptun-client -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" ./client && \
  env CGO_ENABLED=0 go build -o kcptun-server -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" ./server && \
  mv ./kcptun-client ./kcptun-server /tmp/release/ && \
  \
  # Compile gost-plugin
  cd ../gost-plugin/ && \
  git checkout $GOST_PLUGIN -b build && VERSION=`git describe --tags` && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" && \
  mv ./gost-plugin /tmp/release && \
  \
  # Compile GoQuiet
  cd ../GoQuiet/ && VERSION=`git describe --tags` && \
  go mod init github.com/cbeuw/GoQuiet && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/gq-client && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/gq-server && \
  mv ./gq-client ./gq-server /tmp/release/ && \
  \
  # mos-tls-tunnel
  cd ../mos-tls-tunnel/ && \
  go mod init github.com/IrineSistiana/mos-tls-tunnel && go mod vendor && \
  env CGO_ENABLED=0 go build -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-client && \
  env CGO_ENABLED=0 go build -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-server && \
  mv ./mtt-client ./mtt-server /tmp/release/ && \
  \
  # Compile rabbit-plugin
  cd ../rabbit-plugin/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
  mv ./rabbit-plugin /tmp/release/ && \
  \
  # Compile rabbit-tcp
  cd ../rabbit-tcp/ && VERSION=`git describe --tags` && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.Version=$VERSION -s -w" ./cmd/rabbit.go && \
  mv ./rabbit /tmp/release/ && \
  \
  # Compile gun-plugin
  cd ../gun/ && \
  env CGO_ENABLED=0 go build -o gun-plugin -trimpath -ldflags "-s -w" ./cmd/sip003/ && \
  mv ./gun-plugin /tmp/release/

FROM golang:1.17.11-alpine3.16 AS plugin-3
ENV SIMPLE_TLS="v0.7.0"
RUN \
  apk add git && mkdir /tmp/release/ && \
  git clone https://github.com/cbeuw/Cloak.git && \
  git clone https://github.com/teddysun/xray-plugin.git && \
  git clone https://github.com/IrineSistiana/simple-tls.git && \
  \
  # Compile simple-tls
  cd ./simple-tls/ && \
  git checkout $SIMPLE_TLS -b build && VERSION=`git describe --tags` && \
  sed -i 's/version = "unknown\/dev"/version = "'$VERSION'"/g' main.go && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
  mv ./simple-tls /tmp/release/ && \
  \
  # Compile xray-plugin
  cd ../xray-plugin/ && VERSION=`git describe --tags` && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" && \
  mv ./xray-plugin /tmp/release/ && \
  \
  # Compile Cloak
  cd ../Cloak/ && VERSION=`git describe --tags` && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/ck-client && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/ck-server && \
  mv ./ck-client ./ck-server /tmp/release/

FROM python:3.10.5-alpine3.16 AS asset
COPY --from=ss-rust /tmp/release /tmp/release
COPY --from=ss-libev /tmp/release /tmp/release
COPY --from=ss-python /tmp/release /tmp/release
COPY --from=plugin-1 /tmp/release /tmp/release
COPY --from=plugin-2 /tmp/release /tmp/release
COPY --from=plugin-3 /tmp/release /tmp/release
RUN \
  PACKAGE_DIR="usr/local/lib/$(ls /usr/local/lib/ | grep ^python)/site-packages" && \
  mkdir -p /asset/$PACKAGE_DIR/ && \
  cd /asset/$PACKAGE_DIR/ && mv /tmp/release/*.tar.bz2 ./ && \
  ls ./*.tar.bz2 | xargs -n1 tar xf && rm -rf ./*.tar.bz2 && \
  mkdir -p /asset/usr/bin/ && mkdir -p /asset/lib/ && \
  ln -s /$PACKAGE_DIR/ssr-python/local.py /asset/usr/bin/ssr-local && \
  ln -s /$PACKAGE_DIR/ssr-python/server.py /asset/usr/bin/ssr-server && \
  ln -s /$PACKAGE_DIR/ss-python/local.py /asset/usr/bin/ss-python-local && \
  ln -s /$PACKAGE_DIR/ss-python/server.py /asset/usr/bin/ss-python-server && \
  ln -s /$PACKAGE_DIR/ss-python-legacy/local.py /asset/usr/bin/ss-python-legacy-local && \
  ln -s /$PACKAGE_DIR/ss-python-legacy/server.py /asset/usr/bin/ss-python-legacy-server && \
  mv /tmp/release/*.so* /asset/lib/ && \
  mv /tmp/release/* /asset/usr/bin/

FROM python:3.10.5-alpine3.16
COPY --from=asset /asset /
RUN \
  apk add --no-cache c-ares glib libev libsodium mbedtls pcre && \
  pip3 --no-cache-dir install colorlog pysocks requests

# ss-libev-server --help
# ss-libev-local --help
# ss-rust-server --help
# ss-rust-local --help
# ss-bootstrap-server --help
# ss-bootstrap-local --help
# ss-python-server --help
# ss-python-local --help
# ss-python-legacy-server --help
# ss-python-legacy-local --help
# ssr-server --help
# ssr-local --help

# obfs-local --help
# obfs-server --help
# simple-tls --help
# v2ray-plugin --help
# xray-plugin --help
# kcptun-client --help
# kcptun-server --help
# gost-plugin --help
# ck-client --help
# ck-server --help
# gq-client --help
# gq-server --help
# mtt-client --help
# mtt-server --help
# rabbit-plugin --help
# rabbit --help
# qtun-client --help
# qtun-server --help
# gun-plugin --help
