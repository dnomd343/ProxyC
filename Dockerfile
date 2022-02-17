FROM alpine:3.15 as build

ENV SS_LIBEV="3.3.5"
ENV SS_RUST="1.12.5"
ENV SIMPLE_TLS="v0.6.1"
ENV GOST_PLUGIN="v1.6.3"

ENV XRAY_VERSION="v1.5.3"
ENV V2FLY_VERSION="v4.44.0"

ENV GO_VERSION="1.17.6"

RUN \
apk add asciidoc autoconf automake build-base curl c-ares-dev cmake \
        git glib-dev go libev-dev libsodium-dev libtool linux-headers make \
        mbedtls-dev pcre-dev python3 python3-dev py3-pip udns-dev xmlto zlib-dev && \
\
# Get source code of Shadowsocks (python/libev/rust)
cd /tmp/ && mkdir ./release/ && \
git clone https://github.com/dnomd343/shadowsocksr.git && \
git clone https://github.com/shadowsocks/shadowsocks.git && \
git clone https://github.com/dnomd343/shadowsocks-bootstrap.git && \
wget https://github.com/shadowsocks/shadowsocks/archive/refs/tags/2.6.2.tar.gz && \
wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v$SS_LIBEV/shadowsocks-libev-$SS_LIBEV.tar.gz && \
wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v2.6.3/shadowsocks-libev-2.6.3.tar.gz && \
wget https://github.com/shadowsocks/shadowsocks-rust/archive/refs/tags/v$SS_RUST.tar.gz && \
tar xf 2.6.2.tar.gz && \
tar xf shadowsocks-libev-$SS_LIBEV.tar.gz && \
tar xf shadowsocks-libev-2.6.3.tar.gz && \
tar xf v$SS_RUST.tar.gz && \
\
# Get source code of SIP003 plugins
git clone https://github.com/shadowsocks/simple-obfs.git && \
git clone https://github.com/IrineSistiana/simple-tls.git && \
git clone https://github.com/shadowsocks/v2ray-plugin.git && \
git clone https://github.com/teddysun/xray-plugin.git && \
git clone https://github.com/shadowsocks/kcptun.git && \
git clone https://github.com/maskedeken/gost-plugin.git && \
git clone https://github.com/cbeuw/Cloak.git && \
git clone https://github.com/cbeuw/GoQuiet.git && \
git clone https://github.com/IrineSistiana/mos-tls-tunnel.git && \
git clone https://github.com/ihciah/rabbit-plugin.git && \
git clone https://github.com/ihciah/rabbit-tcp.git && \
git clone https://github.com/shadowsocks/qtun.git && \
git clone https://github.com/Qv2ray/gun.git && \
\
# Get source code of Xray-core and v2fly-core
git clone https://github.com/XTLS/Xray-core && \
git clone https://github.com/v2fly/v2ray-core && \
\
# Install rust environment (nightly version)
sh -c "$(curl -sL https://sh.rustup.rs)" @ -y --no-modify-path --default-toolchain nightly && \
\
# Install Go environment (v1.16.13)
wget -O /tmp/go-1.16.13.tar.gz https://dl.google.com/go/go1.16.13.src.tar.gz && \
tar -C /usr/local/ -xf /tmp/go-1.16.13.tar.gz && \
mv /usr/local/go/ /usr/local/go-1.16.13/ && \
cd /usr/local/go-1.16.13/src/ && ./make.bash && \
\
# Install Go environment (latest version)
wget -O /tmp/go-$GO_VERSION.tar.gz https://dl.google.com/go/go$GO_VERSION.src.tar.gz && \
tar -C /usr/local/ -xf /tmp/go-$GO_VERSION.tar.gz && \
mv /usr/local/go/ /usr/local/go-$GO_VERSION/ && \
cd /usr/local/go-$GO_VERSION/src/ && ./make.bash && \
\
# Switch to latest version of Golang
apk del go && \
export PATH=$PATH:/usr/local/go-$GO_VERSION/bin && \
\
# Compile and install openssl (version 1.0.2u)
wget https://www.openssl.org/source/old/1.0.2/openssl-1.0.2u.tar.gz -P /tmp && \
cd /tmp/ && tar xf openssl-1.0.2u.tar.gz && cd ./openssl-1.0.2u/ && \
./config --shared --prefix=/usr && make && make install && \
cp /usr/lib/libcrypto.so.1.0.0 /tmp/release/ && \
\
# Install and package numpy / salsa20 / flask / IPy / redis / pysocks / requests
pip install numpy salsa20 flask IPy redis pysocks && \
mkdir /tmp/packages/ && cd /tmp/packages/ && \
PACKAGE_DIR=/usr/lib/`ls /usr/lib/ | grep ^python`/site-packages && \
cp -r $PACKAGE_DIR/*certifi* ./ && \
cp -r $PACKAGE_DIR/*charset* ./ && \
cp -r $PACKAGE_DIR/*click* ./ && \
cp -r $PACKAGE_DIR/*deprecated* ./ && \
cp -r $PACKAGE_DIR/*Deprecated* ./ && \
cp -r $PACKAGE_DIR/*flask* ./ && \
cp -r $PACKAGE_DIR/*Flask* ./ && \
cp -r $PACKAGE_DIR/*idna* ./ && \
cp -r $PACKAGE_DIR/*IPy* ./ && \
cp -r $PACKAGE_DIR/*itsdangerous* ./ && \
cp -r $PACKAGE_DIR/*Jinja2* ./ && \
cp -r $PACKAGE_DIR/*jinja2* ./ && \
cp -r $PACKAGE_DIR/*Jinja2* ./ && \
cp -r $PACKAGE_DIR/*markupsafe* ./ && \
cp -r $PACKAGE_DIR/*MarkupSafe* ./ && \
cp -r $PACKAGE_DIR/*numpy* ./ && \
cp -r $PACKAGE_DIR/*packaging* ./ && \
cp -r $PACKAGE_DIR/*PySocks* ./ && \
cp -r $PACKAGE_DIR/*redis* ./ && \
cp -r $PACKAGE_DIR/*requests* ./ && \
cp -r $PACKAGE_DIR/*salsa20* ./ && \
cp -r $PACKAGE_DIR/*socks* ./ && \
cp -r $PACKAGE_DIR/*urllib3* ./ && \
cp -r $PACKAGE_DIR/*werkzeug* ./ && \
cp -r $PACKAGE_DIR/*Werkzeug* ./ && \
cp -r $PACKAGE_DIR/*wrapt* ./ && \
rm -rf `find ./ -name '__pycache__'` && \
strip `find ./ -name '*.so'` && \
cd ../ && tar czf packages.tar.gz ./packages/ && \
mv packages.tar.gz ./release/ && \
\
# Package shadowsocksr
cd /tmp/shadowsocksr/ && \
sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
sed -i "/for path in paths:/a\        if (path.startswith('libcrypto.so')):" ./shadowsocks/crypto/util.py && \
sed -i "/startswith/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py && \
python3 setup.py build && cd ./build/ && mv ./lib/ ./ssr-python/ && \
mv ./ssr-python/shadowsocks/local.py ./ssr-python/shadowsocks/server.py ./ssr-python/ && \
chmod +x ./ssr-python/local.py ./ssr-python/server.py && \
BZIP2=-9 tar cjf /tmp/release/ssr-python.tar.bz2 ./ssr-python/ && \
\
# Package shadowsocks-python
cd /tmp/shadowsocks/ && git checkout master && rm -rf ./.git && \
python3 setup.py build && cd ./build/ && mv ./lib/ ./ss-python/ && \
mv ./ss-python/shadowsocks/local.py ./ss-python/shadowsocks/server.py ./ss-python/ && \
chmod +x ./ss-python/local.py ./ss-python/server.py && \
BZIP2=-9 tar cjf /tmp/release/ss-python.tar.bz2 ./ss-python/ && \
\
# Package shadowsocks-python-2.6.2
cd /tmp/shadowsocks-2.6.2/ && \
sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
python3 setup.py build && cd ./build/ && mv ./lib/ ./ss-python-legacy/ && \
mv ./ss-python-legacy/shadowsocks/local.py ./ss-python-legacy/shadowsocks/server.py ./ss-python-legacy/ && \
chmod +x ./ss-python-legacy/local.py ./ss-python-legacy/server.py && \
BZIP2=-9 tar cjf /tmp/release/ss-python-legacy.tar.bz2 ./ss-python-legacy/ && \
\
# Compile shadowsocks-bootstrap
cd /tmp/shadowsocks-bootstrap/ && mkdir ./build/ && \
cd ./build/ && cmake -DCMAKE_BUILD_TYPE=Release .. && make && \
mv ../bin/* /tmp/release/ && \
\
# Compile shadowsocks-libev-2.6.3
cd /tmp/shadowsocks-libev-2.6.3/ && \
sed -i '/ss-nat/d' `grep "ss-nat" -rl src/*` && \
sed -i 's/^const protocol_t/extern const protocol_t/g' `grep "^const protocol" -rl src/*.h` && \
./configure --prefix=/usr && make && make install && \
mv /usr/bin/ss-local /tmp/release/ss-libev-legacy-local && \
mv /usr/bin/ss-server /tmp/release/ss-libev-legacy-server && \
\
# Compile shadowsocks-libev (latest version)
apk add --no-cache --virtual .build-deps libsodium-dev openssl-dev && \
cd /tmp/shadowsocks-libev-$SS_LIBEV/ && \
./configure --prefix=/usr && make && make install && \
mv /usr/bin/ss-local /tmp/release/ss-libev-local && \
mv /usr/bin/ss-server /tmp/release/ss-libev-server && \
apk del .build-deps && \
\
# Compile shadowsocks-rust
cd /tmp/shadowsocks-rust-$SS_RUST/ && \
/root/.cargo/bin/cargo build --release && \
mv ./target/release/sslocal /tmp/release/ss-rust-local && \
mv ./target/release/ssserver /tmp/release/ss-rust-server && \
\
# Compile simple-obfs
cd /tmp/simple-obfs/ && \
git submodule update --init --recursive && \
./autogen.sh && ./configure && make && make install && \
cp /usr/local/bin/obfs-local /usr/local/bin/obfs-server /tmp/release/ && \
\
# Compile simple-tls
cd /tmp/simple-tls/ && \
git checkout $SIMPLE_TLS -b build && VERSION=`git describe --tags` && \
sed -i 's/version = "unknown\/dev"/version = "'$VERSION'"/g' main.go && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
mv ./simple-tls /tmp/release/ && \
\
# Compile xray-plugin
cd /tmp/xray-plugin/ && VERSION=`git describe --tags` && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" && \
mv ./xray-plugin /tmp/release/ && \
\
# Compile Cloak
cd /tmp/Cloak/ && VERSION=`git describe --tags` && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/ck-client && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/ck-server && \
mv ./ck-client ./ck-server /tmp/release/ && \
\
# Compile Xray-core
cd /tmp/Xray-core && git checkout $XRAY_VERSION && \
env CGO_ENABLED=0 go build -o xray -trimpath -ldflags "-s -w" ./main && \
mv ./xray /tmp/release/ && \
\
# Compile v2fly-core
cd /tmp/v2ray-core && git checkout $V2FLY_VERSION && \
env CGO_ENABLED=0 go build -o v2ray -trimpath -ldflags "-s -w" ./main && \
env CGO_ENABLED=0 go build -o v2ctl -trimpath -ldflags "-s -w" -tags confonly ./infra/control/main && \
mv ./v2ctl ./v2ray /tmp/release/ && \
\
# Switch to go 1.16.13
export PATH=/usr/local/go-1.16.13/bin:$PATH && \
\
# Compile v2ray-plugin
cd /tmp/v2ray-plugin/ && VERSION=`git describe --tags` && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" && \
mv ./v2ray-plugin /tmp/release/ && \
\
# Compile kcptun
cd /tmp/kcptun/ && git checkout sip003 && VERSION=`git describe --tags` && \
go mod init github.com/shadowsocks/kcptun && go mod tidy && \
env CGO_ENABLED=0 go build -o kcptun-client -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" ./client && \
env CGO_ENABLED=0 go build -o kcptun-server -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" ./server && \
mv ./kcptun-client ./kcptun-server /tmp/release/ && \
\
# Compile gost-plugin
cd /tmp/gost-plugin/ && \
git checkout $GOST_PLUGIN -b build && VERSION=`git describe --tags` && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$VERSION -s -w" && \
mv ./gost-plugin /tmp/release && \
\
# Compile GoQuiet
cd /tmp/GoQuiet/ && VERSION=`git describe --tags` && \
go mod init github.com/cbeuw/GoQuiet && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/gq-client && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$VERSION -s -w" ./cmd/gq-server && \
mv ./gq-client ./gq-server /tmp/release/ && \
\
# mos-tls-tunnel
cd /tmp/mos-tls-tunnel/ && \
go mod init github.com/IrineSistiana/mos-tls-tunnel && go mod vendor && \
env CGO_ENABLED=0 go build -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-client && \
env CGO_ENABLED=0 go build -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-server && \
mv ./mtt-client ./mtt-server /tmp/release/ && \
\
# Compile rabbit-plugin
cd /tmp/rabbit-plugin/ && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
mv ./rabbit-plugin /tmp/release/ && \
\
# Compile rabbit-tcp
cd /tmp/rabbit-tcp/ && VERSION=`git describe --tags` && \
env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.Version=$VERSION -s -w" ./cmd/rabbit.go && \
mv ./rabbit /tmp/release/ && \
\
# Compile gun-plugin
cd /tmp/gun/ && \
env CGO_ENABLED=0 go build -o gun-plugin -trimpath -ldflags "-s -w" ./cmd/sip003/ && \
mv ./gun-plugin /tmp/release/ && \
\
# Compile qtun
cd /tmp/qtun/ && \
/root/.cargo/bin/cargo build --release && \
mv ./target/release/qtun-client /tmp/release/ && \
mv ./target/release/qtun-server /tmp/release/

FROM alpine:3.15 as asset
COPY --from=build /tmp/release/ /tmp/release/
RUN apk add gcc python3 upx && \
cd /tmp/ && mkdir ./bin/ && mkdir ./lib/ && \
mv ./release/packages.tar.gz ./ && tar xf packages.tar.gz && \
mv /tmp/release/*.tar.bz2 /tmp/packages/ && \
mv /tmp/release/*.so* /tmp/lib/ && \
mv /tmp/release/* /tmp/bin && \
cd /tmp/bin/ && strip * && upx -9 * && \
cd /tmp/lib/ && strip * && \
cd /tmp/packages/ && \
tar xf ssr-python.tar.bz2 && rm -f ./ssr-python.tar.bz2 && \
tar xf ss-python.tar.bz2 && rm -f ./ss-python.tar.bz2 && \
tar xf ss-python-legacy.tar.bz2 && rm -f ./ss-python-legacy.tar.bz2 && \
PYTHON_DIR=`ls /usr/lib/ | grep ^python` && \
mkdir -p /tmp/lib/$PYTHON_DIR/ && \
mv /tmp/packages/ /tmp/lib/$PYTHON_DIR/site-packages/

FROM alpine:3.15
COPY . /usr/local/share/ProxyC
COPY --from=asset /tmp/bin/ /usr/bin/
COPY --from=asset /tmp/lib/ /usr/lib/
RUN apk add --no-cache c-ares glib libev libsodium mbedtls pcre python3 redis udns && \
echo "daemonize yes" >> /etc/redis.conf && \
PKG_DIR=/usr/lib/`ls /usr/lib/ | grep ^python`/site-packages && \
rm -rf `find /usr/lib/ -name '__pycache__'` && \
ln -s $PKG_DIR/ssr-python/local.py /usr/bin/ssr-local && \
ln -s $PKG_DIR/ssr-python/server.py /usr/bin/ssr-server && \
ln -s $PKG_DIR/ss-python/local.py /usr/bin/ss-python-local && \
ln -s $PKG_DIR/ss-python/server.py /usr/bin/ss-python-server && \
ln -s $PKG_DIR/ss-python-legacy/local.py /usr/bin/ss-python-legacy-local && \
ln -s $PKG_DIR/ss-python-legacy/server.py /usr/bin/ss-python-legacy-server && \
ln -s /usr/bin/python3 /usr/bin/python
EXPOSE 43581
