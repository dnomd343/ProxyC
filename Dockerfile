# Compile shadowsocks-rust
FROM rust:1.62-alpine3.16 AS ss-rust
ENV SS_RUST="v1.15.0-alpha.8"
RUN \
  apk add build-base && \
  wget https://github.com/shadowsocks/shadowsocks-rust/archive/refs/tags/${SS_RUST}.tar.gz && \
  tar xf ${SS_RUST}.tar.gz && cd ./shadowsocks-rust-*/ && \
  cargo build --release --features "stream-cipher aead-cipher-extra aead-cipher-2022 aead-cipher-2022-extra" && \
  cd ./target/release/ && mv ./sslocal /tmp/ss-rust-local && mv ./ssserver /tmp/ss-rust-server

# Compile shadowsocks-libev
FROM alpine:3.16 AS ss-libev
ENV SS_LIBEV="3.3.5"
RUN \
  apk add build-base c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev && \
  wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v${SS_LIBEV}/shadowsocks-libev-${SS_LIBEV}.tar.gz && \
  tar xf shadowsocks-libev-*.tar.gz && cd ./shadowsocks-libev-*/ && \
  ./configure --disable-documentation --prefix=/usr && make && make install && \
  cd /usr/bin && mv ./ss-local /tmp/ss-libev-local && mv ./ss-server /tmp/ss-libev-server

# Package shadowsocks-python (lastest version, legacy version, R version aka ssr)
FROM python:3.10-alpine3.16 AS ss-python
ENV SS_PYTHON_LEGACY="2.6.2"
RUN \
  apk add git && mkdir /packages/ && \
  git clone https://github.com/dnomd343/shadowsocksr.git && \
  git clone https://github.com/shadowsocks/shadowsocks.git && \
  wget https://github.com/shadowsocks/shadowsocks/archive/refs/tags/${SS_PYTHON_LEGACY}.tar.gz && \
  tar xf ${SS_PYTHON_LEGACY}.tar.gz
# shadowsocks-python (R version)
RUN \
  cd ./shadowsocksr/ && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/ordereddict.py && \
  sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
  sed -i "/for path in paths:/a\        if 'libcrypto.so' in path:" ./shadowsocks/crypto/util.py && \
  sed -i "/libcrypto.so/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py && \
  python3 setup.py build && cd ./build/lib/shadowsocks/ && \
  chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
  mv ../../lib/ /packages/ssr-python/
# shadowsocks-python (latest version)
RUN \
  cd ./shadowsocks/ && git checkout master && \
  sed -i 's/if addr is/if addr ==/g' ./shadowsocks/common.py && \
  sed -i 's/and ip is not/and ip !=/g' ./shadowsocks/common.py && \
  sed -i 's/if len(block) is/if len(block) ==/g' ./shadowsocks/common.py && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
  python3 setup.py build && cd ./build/lib/shadowsocks/ && \
  chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
  mv ../../lib/ /packages/ss-python/
# shadowsocks-python (legacy version)
RUN \
  cd ./shadowsocks-${SS_PYTHON_LEGACY}/ && \
  sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
  sed -i "s/find_library(p)/'libsodium.so.23'/g" ./shadowsocks/crypto/ctypes_libsodium.py && \
  sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
  python3 setup.py build && cd ./build/lib/shadowsocks/ && \
  chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
  mv ../../lib/ /packages/ss-python-legacy/

# Compile shadowsocks-bootstrap
FROM alpine:3.16 AS ss-bootstrap
RUN \
  apk add build-base cmake git glib-dev && \
  git clone https://github.com/dnomd343/shadowsocks-bootstrap.git && \
  cd ./shadowsocks-bootstrap/ && mkdir ./build/ && cd ./build/ && \
  cmake -DCMAKE_BUILD_TYPE=Release .. && make && \
  mv ../bin/ss-bootstrap-* /tmp/

# Compile openssl (old version, for shadowsocks method -> idea-cfb / seed-cfb)
FROM alpine:3.16 AS openssl
ENV OPENSSL_VER="1.0.2"
ENV OPENSSL_SUB_VER="u"
RUN \
  apk add build-base perl && \
  wget https://www.openssl.org/source/old/${OPENSSL_VER}/openssl-${OPENSSL_VER}${OPENSSL_SUB_VER}.tar.gz && \
  tar xf openssl-*.tar.gz && cd ./openssl-*/ && \
  ./config --shared --prefix=/usr && make && \
  mv ./libcrypto.so.1.0.0 /tmp/

# Build numpy and salsa20 python module
FROM python:3.10-alpine3.16 AS salsa20
RUN \
  apk add build-base && \
  pip3 install numpy salsa20 && \
  cd /usr/local/lib/python*/site-packages/ && \
  mkdir /packages/ && mv ./*numpy* ./*salsa20* /packages/ && \
  rm -rf $(find /packages/ -name '__pycache__')

# Combine shadowsocks dependencies
FROM python:3.10-alpine3.16 AS shadowsocks
COPY --from=ss-rust /tmp/ss-rust-* /release/
COPY --from=ss-libev /tmp/ss-libev-* /release/
COPY --from=ss-python /packages/ /site-packages/
COPY --from=ss-bootstrap /tmp/ss-bootstrap-* /release/
COPY --from=openssl /tmp/libcrypto.so* /release/
COPY --from=salsa20 /packages/ /site-packages/
RUN \
  PYTHON_PACKAGE="/usr/local/lib/$(ls /usr/local/lib/ | grep ^python)/site-packages" && \
  ln -s ${PYTHON_PACKAGE}/ssr-python/local.py /release/ssr-local && \
  ln -s ${PYTHON_PACKAGE}/ssr-python/server.py /release/ssr-server && \
  ln -s ${PYTHON_PACKAGE}/ss-python/local.py /release/ss-python-local && \
  ln -s ${PYTHON_PACKAGE}/ss-python/server.py /release/ss-python-server && \
  ln -s ${PYTHON_PACKAGE}/ss-python-legacy/local.py /release/ss-python-legacy-local && \
  ln -s ${PYTHON_PACKAGE}/ss-python-legacy/server.py /release/ss-python-legacy-server && \
  BZIP2=-9 tar cjf /release/packages.tar.bz2 ./site-packages/

# Compile sip003 plugins (part1 -> gcc & cargo)
FROM rust:1.62-alpine3.16 AS plugin-1
RUN \
  apk add git && mkdir /plugins/ && \
  git clone https://github.com/shadowsocks/simple-obfs.git && \
  git clone https://github.com/shadowsocks/qtun.git
# Compile simple-obfs
RUN \
  apk add autoconf automake build-base libev-dev libtool linux-headers && \
  cd ./simple-obfs/ && git submodule update --init --recursive && \
  ./autogen.sh && ./configure --disable-documentation && make && \
  cd ./src/ && mv ./obfs-local ./obfs-server /plugins/
# Compile qtun
RUN \
  cd ./qtun/ && cargo build --release && \
  cd ./target/release/ && mv ./qtun-client ./qtun-server /plugins/

# Compile sip003 plugins (part2 -> go1.16)
FROM golang:1.16-alpine3.15 AS plugin-2
ENV GOST_PLUGIN="v1.6.3"
RUN \
  apk add git && mkdir /plugins/ && \
  git clone https://github.com/Qv2ray/gun.git && \
  git clone https://github.com/dnomd343/kcptun.git && \
  git clone https://github.com/dnomd343/GoQuiet.git && \
  git clone https://github.com/ihciah/rabbit-tcp.git && \
  git clone https://github.com/dnomd343/rabbit-plugin.git && \
  git clone https://github.com/maskedeken/gost-plugin.git && \
  git clone https://github.com/shadowsocks/v2ray-plugin.git && \
  git clone https://github.com/IrineSistiana/mos-tls-tunnel.git
# Compile v2ray-plugin
RUN \
  cd ./v2ray-plugin/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
  mv ./v2ray-plugin /plugins/
# Compile kcptun
RUN \
  cd ./kcptun/ && git checkout sip003 && \
  go mod init github.com/shadowsocks/kcptun && go mod tidy && \
  env CGO_ENABLED=0 go build -o kcptun-client -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./client && \
  env CGO_ENABLED=0 go build -o kcptun-server -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./server && \
  mv ./kcptun-client ./kcptun-server /plugins/
# Compile gost-plugin
RUN \
  cd ./gost-plugin/ && \
  git checkout ${GOST_PLUGIN} -b build && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
  mv ./gost-plugin /plugins/
# Compile GoQuiet
RUN \
  cd ./GoQuiet/ && \
  go mod init github.com/cbeuw/GoQuiet && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-client && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-server && \
  mv ./gq-client ./gq-server /plugins/
# Compile mos-tls-tunnel
RUN \
  cd ./mos-tls-tunnel/ && \
  go mod init github.com/IrineSistiana/mos-tls-tunnel && go mod vendor && \
  env CGO_ENABLED=0 go build -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-client && \
  env CGO_ENABLED=0 go build -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-server && \
  mv ./mtt-client ./mtt-server /plugins/
# Compile rabbit-plugin
RUN \
  cd ./rabbit-plugin/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
  mv ./rabbit-plugin /plugins/
# Compile rabbit-tcp
RUN \
  cd ./rabbit-tcp/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.Version=$(git describe --tags) -s -w" ./cmd/rabbit.go && \
  mv ./rabbit /plugins/
# Compile gun-plugin
RUN \
  cd ./gun/ && \
  env CGO_ENABLED=0 go build -o gun-plugin -trimpath -ldflags "-s -w" ./cmd/sip003/ && \
  mv ./gun-plugin /plugins/

# Compile sip003 plugins (part3 -> go1.17)
FROM golang:1.17-alpine3.16 AS plugin-3
ENV SIMPLE_TLS="v0.7.0"
RUN \
  apk add git && mkdir /plugins/ && \
  git clone https://github.com/cbeuw/Cloak.git && \
  git clone https://github.com/teddysun/xray-plugin.git && \
  git clone https://github.com/IrineSistiana/simple-tls.git
# Compile simple-tls
RUN \
  cd ./simple-tls/ && \
  git checkout ${SIMPLE_TLS} -b build && \
  sed -i 's/version = "unknown\/dev"/version = "'$(git describe --tags)'"/g' main.go && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
  mv ./simple-tls /plugins/
# Compile xray-plugin
RUN \
  cd ./xray-plugin/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
  mv ./xray-plugin /plugins/
# Compile Cloak
RUN \
  cd ./Cloak/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-client && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-server && \
  mv ./ck-client ./ck-server /plugins/

# Combine sip003 plugins
FROM busybox AS plugin
COPY --from=plugin-1 /plugins/ /release/
COPY --from=plugin-2 /plugins/ /release/
COPY --from=plugin-3 /plugins/ /release/

# Combine all release
FROM python:3.10-alpine3.16 AS asset
COPY --from=shadowsocks /release/ /release/
COPY --from=plugin /release/ /release/
RUN \
  PACKAGE_DIR="/asset/usr/local/lib/$(ls /usr/local/lib/ | grep ^python)" && \
  mkdir -p ${PACKAGE_DIR}/ && tar xf /release/packages.tar.bz2 -C ${PACKAGE_DIR}/ && \
  mkdir -p /asset/lib/ && mv /release/*.so* /asset/lib/ && \
  rm -f /release/packages.tar.bz2 && \
  mv /release/ /asset/usr/bin/

# Release docker image
FROM python:3.10-alpine3.16
COPY --from=asset /asset /
RUN \
  apk add --no-cache c-ares glib libev libsodium mbedtls pcre && \
  pip3 --no-cache-dir install colorlog pysocks requests
