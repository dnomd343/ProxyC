FROM alpine:3.16.0 AS ss-libev
ENV SS_LIBEV="3.3.5"
ENV SS_LIBEV_LEGACY="2.6.3"
RUN \
  # Source code downloads and dependent installations
  apk add asciidoc build-base c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev udns-dev xmlto zlib-dev && \
  wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v$SS_LIBEV/shadowsocks-libev-$SS_LIBEV.tar.gz && \
  wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v$SS_LIBEV_LEGACY/shadowsocks-libev-$SS_LIBEV_LEGACY.tar.gz && \
  wget https://www.openssl.org/source/old/1.0.2/openssl-1.0.2u.tar.gz && \
  ls ./*.tar.gz | xargs -n1 tar xf && \
  mkdir -p /tmp/release/ && \
  \
  # Compile shadowsocks-libev (latest version)
  cd ./shadowsocks-libev-$SS_LIBEV/ && \
  ./configure --prefix=/usr && make && make install && \
  mv /usr/bin/ss-local /tmp/release/ss-libev-local && \
  mv /usr/bin/ss-server /tmp/release/ss-libev-server && \
  \
  # Compile and install openssl (version 1.0.2u)
  cd ../openssl-1.0.2u/ && \
  ./config --shared --prefix=/usr && make && make install && \
  cp /usr/lib/libcrypto.so.1.0.0 /tmp/release/ && \
  \
  # Compile shadowsocks-libev (legacy version)
  cd ../shadowsocks-libev-$SS_LIBEV_LEGACY/ && \
  sed -i '/ss-nat/d' `grep "ss-nat" -rl src/*` && \
  sed -i 's/^const protocol_t/extern const protocol_t/g' `grep "^const protocol" -rl src/*.h` && \
  ./configure --prefix=/usr && make && make install && \
  mv /usr/bin/ss-local /tmp/release/ss-libev-legacy-local && \
  mv /usr/bin/ss-server /tmp/release/ss-libev-legacy-server

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
  sed -i "/for path in paths:/a\        if (path.startswith('libcrypto.so')):" ./shadowsocks/crypto/util.py && \
  sed -i "/startswith/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py && \
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
  sed -i "s/find_library(p)/'libsodium.so'/g" ./shadowsocks/crypto/ctypes_libsodium.py && \
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

FROM python:3.10.5-alpine3.16 AS asset
COPY --from=ss-rust /tmp/release /tmp/release
COPY --from=ss-libev /tmp/release /tmp/release
COPY --from=ss-python /tmp/release /tmp/release
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
  apk add --no-cache c-ares glib libev libsodium mbedtls pcre udns
# ss-libev-server --help
# ss-libev-local --help
# ss-libev-legacy-server --help
# ss-libev-legacy-local --help
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
