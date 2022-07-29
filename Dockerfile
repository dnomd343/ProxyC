# Compile upx (can't use gcc11 for now)
FROM alpine:3.15 AS upx
ENV UPX_VERSION="3.96"
RUN \
  apk add bash build-base perl ucl-dev zlib-dev && \
  wget https://github.com/upx/upx/releases/download/v${UPX_VERSION}/upx-${UPX_VERSION}-src.tar.xz
RUN \
  tar xf upx-${UPX_VERSION}-src.tar.xz && \
  cd upx-${UPX_VERSION}-src/ && make all && \
  mv ./src/upx.out /usr/bin/upx
RUN \
  mkdir -p /upx/lib/ && mkdir -p /upx/bin/ && cd /upx/ && \
  cp -d /usr/lib/libgcc_s.so* /usr/lib/libstdc++.so* /usr/lib/libucl.so* ./lib/ && \
  cp /usr/bin/upx ./bin/

# Compile shadowsocks-rust
FROM rust:1.62-alpine3.16 AS ss-rust
ENV SS_RUST="v1.15.0-alpha.8"
RUN \
  apk add build-base && \
  wget https://github.com/shadowsocks/shadowsocks-rust/archive/refs/tags/${SS_RUST}.tar.gz
RUN \
  tar xf ${SS_RUST}.tar.gz && cd ./shadowsocks-rust-*/ && \
  cargo build --release --bin sslocal --bin ssserver  \
    --features "stream-cipher aead-cipher-extra aead-cipher-2022 aead-cipher-2022-extra" && \
  cd ./target/release/ && mv ./sslocal /tmp/ss-rust-local && mv ./ssserver /tmp/ss-rust-server
COPY --from=upx /upx/ /usr/
RUN strip /tmp/ss-rust-* && upx -9 /tmp/ss-rust-*

# Compile shadowsocks-libev
FROM alpine:3.16 AS ss-libev
ENV SS_LIBEV="3.3.5"
RUN \
  apk add build-base c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev && \
  wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v${SS_LIBEV}/shadowsocks-libev-${SS_LIBEV}.tar.gz
RUN \
  tar xf shadowsocks-libev-*.tar.gz && cd ./shadowsocks-libev-*/ && \
  ./configure --disable-documentation && make && \
  mv ./src/ss-local /tmp/ss-libev-local && mv ./src/ss-server /tmp/ss-libev-server
RUN strip /tmp/ss-libev-*

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
  git clone https://github.com/dnomd343/shadowsocks-bootstrap.git
RUN \
  cd ./shadowsocks-bootstrap/ && mkdir ./build/ && cd ./build/ && \
  cmake -DCMAKE_BUILD_TYPE=Release .. && make && \
  mv ../bin/ss-bootstrap-* /tmp/
RUN strip /tmp/ss-bootstrap-*

# Combine shadowsocks dependencies
FROM python:3.10-alpine3.16 AS shadowsocks
COPY --from=ss-rust /tmp/ss-rust-* /release/
COPY --from=ss-libev /tmp/ss-libev-* /release/
COPY --from=ss-bootstrap /tmp/ss-bootstrap-* /release/
RUN \
  PYTHON_PACKAGE="/usr/local/lib/$(ls /usr/local/lib/ | grep ^python)/site-packages" && \
  ln -s ${PYTHON_PACKAGE}/ssr-python/local.py /release/ssr-local && \
  ln -s ${PYTHON_PACKAGE}/ssr-python/server.py /release/ssr-server && \
  ln -s ${PYTHON_PACKAGE}/ss-python/local.py /release/ss-python-local && \
  ln -s ${PYTHON_PACKAGE}/ss-python/server.py /release/ss-python-server && \
  ln -s ${PYTHON_PACKAGE}/ss-python-legacy/local.py /release/ss-python-legacy-local && \
  ln -s ${PYTHON_PACKAGE}/ss-python-legacy/server.py /release/ss-python-legacy-server

# Compile openssl (old version, for shadowsocks method -> idea-cfb / seed-cfb)
FROM alpine:3.16 AS openssl
ENV OPENSSL_VER="1.0.2"
ENV OPENSSL_SUB_VER="u"
RUN \
  apk add build-base perl && \
  wget https://www.openssl.org/source/old/${OPENSSL_VER}/openssl-${OPENSSL_VER}${OPENSSL_SUB_VER}.tar.gz
RUN \
  tar xf openssl-*.tar.gz && cd ./openssl-*/ && \
  ./config --shared --prefix=/usr && make && \
  mv ./libcrypto.so.1.0.0 /tmp/
RUN strip /tmp/libcrypto.so.1.0.0

# Build python module (numpy salsa20 psutil)
FROM python:3.10-alpine3.16 AS python-pkg
RUN apk add build-base linux-headers
RUN \
  pip3 install numpy salsa20 psutil && \
  cd /usr/local/lib/python*/site-packages/ && \
  mkdir /site-packages/ && mv ./*numpy* ./*salsa20* ./psutil* /site-packages/ && \
  rm -rf $(find /site-packages/ -name '__pycache__')
COPY --from=ss-python /packages/ /site-packages/
RUN BZIP2=-9 tar czf /packages.tar.gz ./site-packages/

# Compile sip003 plugins (part1 -> gcc & cargo)
FROM rust:1.62-alpine3.16 AS plugin-1
RUN \
  apk add git && mkdir /plugins/ && \
  git clone https://github.com/shadowsocks/qtun.git && \
  git clone https://github.com/shadowsocks/simple-obfs.git
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
COPY --from=upx /upx/ /usr/
RUN strip /plugins/* && upx -9 /plugins/qtun-*

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
  cd ./gost-plugin/ && git checkout ${GOST_PLUGIN} && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
  mv ./gost-plugin /plugins/
# Compile GoQuiet
RUN \
  cd ./GoQuiet/ && go mod init github.com/cbeuw/GoQuiet && \
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
COPY --from=upx /upx/ /usr/
RUN upx -9 /plugins/*

# Compile sip003 plugins (part3 -> go1.17)
FROM golang:1.17-alpine3.16 AS plugin-3
ENV SIMPLE_TLS="v0.7.0"
ENV CLOAK="v2.6.0"
RUN \
  apk add git && mkdir /plugins/ && \
  git clone https://github.com/cbeuw/Cloak.git && \
  git clone https://github.com/teddysun/xray-plugin.git && \
  git clone https://github.com/IrineSistiana/simple-tls.git
# Compile simple-tls
RUN \
  cd ./simple-tls/ && git checkout ${SIMPLE_TLS} && \
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
  cd ./Cloak/ && git checkout ${CLOAK} && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-client && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-server && \
  mv ./ck-client ./ck-server /plugins/
COPY --from=upx /upx/ /usr/
RUN upx -9 /plugins/*

# Combine sip003 plugins
FROM alpine:3.16 AS plugin
COPY --from=plugin-1 /plugins/ /release/
COPY --from=plugin-2 /plugins/ /release/
COPY --from=plugin-3 /plugins/ /release/

# Compile v2fly-core
FROM golang:1.18-alpine3.16 AS v2ray
ENV V2RAY_VERSION="v4.45.2"
RUN \
  wget https://github.com/v2fly/v2ray-core/archive/refs/tags/${V2RAY_VERSION}.tar.gz && \
  tar xf ${V2RAY_VERSION}.tar.gz && cd ./v2ray-core-*/ && \
  env CGO_ENABLED=0 go build -o v2ray -trimpath -ldflags "-s -w" ./main && \
  env CGO_ENABLED=0 go build -o v2ctl -trimpath -ldflags "-s -w" -tags confonly ./infra/control/main && \
  mv ./v2ctl ./v2ray /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/v2*

# Compile xray-core
FROM golang:1.18-alpine3.16 AS xray
ENV XRAY_VERSION="v1.5.9"
RUN \
  wget https://github.com/XTLS/Xray-core/archive/refs/tags/${XRAY_VERSION}.tar.gz && \
  tar xf ${XRAY_VERSION}.tar.gz && cd ./Xray-core-*/ && \
  env CGO_ENABLED=0 go build -o xray -trimpath -ldflags "-s -w" ./main && \
  mv ./xray /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/xray

# Compile trojan-go
FROM golang:1.17-alpine3.16 AS trojan-go
ENV TROJAN_GO_VERSION="v0.10.6"
RUN \
  apk add git && \
  git clone https://github.com/p4gefau1t/trojan-go.git && \
  cd ./trojan-go/ && git checkout ${TROJAN_GO_VERSION} && \
  env CGO_ENABLED=0 go build -trimpath \
    -ldflags "-X github.com/p4gefau1t/trojan-go/constant.Version=$(git describe --dirty) \
    -X github.com/p4gefau1t/trojan-go/constant.Commit=$(git rev-parse HEAD) -s -w" -tags "full" && \
  mv ./trojan-go /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/trojan-go

# Compile trojan
FROM alpine:3.16 AS trojan
ENV TROJAN_VERSION="v1.16.0"
RUN \
  apk add boost-dev build-base cmake openssl-dev && \
  wget https://github.com/trojan-gfw/trojan/archive/refs/tags/${TROJAN_VERSION}.tar.gz
RUN \
  tar xf ${TROJAN_VERSION}.tar.gz && cd ./trojan-*/ && \
  mkdir ./build/ && cd ./build/ && cmake .. -DENABLE_MYSQL=OFF -DSYSTEMD_SERVICE=OFF && make && \
  mv ./trojan /tmp/
RUN strip /tmp/trojan
COPY --from=trojan-go /tmp/trojan-go /tmp/

# Compile gost-v3
FROM golang:1.18-alpine3.16 AS gost-v3
RUN \
  apk add git && \
  git clone https://github.com/go-gost/gost.git && cd ./gost/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" ./cmd/gost && \
  mv ./gost /tmp/gost-v3
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/gost-v3

# Compile gost
FROM golang:1.17-alpine3.16 AS gost
ENV GOST_VERSION="v2.11.2"
RUN \
  wget https://github.com/ginuerzh/gost/archive/refs/tags/${GOST_VERSION}.tar.gz && \
  tar xf ${GOST_VERSION}.tar.gz && cd ./gost-*/cmd/gost/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" && \
  mv ./gost /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/gost
COPY --from=gost-v3 /tmp/gost-v3 /tmp/

# Compile brook
FROM golang:1.16-alpine3.15 AS brook
ENV BROOK_VERSION="v20220707"
RUN \
  wget https://github.com/txthinking/brook/archive/refs/tags/${BROOK_VERSION}.tar.gz && \
  tar xf ${BROOK_VERSION}.tar.gz && cd ./brook-*/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" ./cli/brook && \
  mv ./brook /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/brook

# Compile clash
FROM golang:1.18-alpine3.16 AS clash
ENV CLASH_VERSION="v1.11.4"
RUN \
  wget https://github.com/Dreamacro/clash/archive/refs/tags/${CLASH_VERSION}.tar.gz && \
  tar xf ${CLASH_VERSION}.tar.gz && cd ./clash-*/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w \
    -X 'github.com/Dreamacro/clash/constant.Version=${CLASH_VERSION}' \
    -X 'github.com/Dreamacro/clash/constant.BuildTime=$(date -u)'" && \
  mv ./clash /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/clash

# Compile caddy
FROM golang:1.18-alpine3.16 AS caddy
RUN \
  go install github.com/caddyserver/xcaddy/cmd/xcaddy@latest && \
  xcaddy build --with github.com/caddyserver/forwardproxy@caddy2=github.com/klzgrad/forwardproxy@naive && \
  mv ./caddy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/caddy

# Download naiveproxy
FROM alpine:3.16 AS naiveproxy
ENV NAIVE_VERSION="v103.0.5060.53-3"
RUN \
  apk add curl libgcc jq && \
  curl -sL https://api.github.com/repos/klzgrad/naiveproxy/releases/tags/${NAIVE_VERSION} | jq .assets | jq .[].name \
    | grep naiveproxy-${NAIVE_VERSION}-openwrt-$(uname -m) | cut -b 2- | rev | cut -b 2- | rev | tac > list.dat
RUN \
  echo -e "while read FILE_NAME;do\nwget https://github.com/klzgrad/naiveproxy/releases/download/\${NAIVE_VERSION}/\${FILE_NAME}\n \
    tar xf \${FILE_NAME} && ldd ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive\n \
    [ \$? -eq 0 ] && cp ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive /tmp/ && break\ndone < list.dat" > naiveproxy.sh && \
  sh naiveproxy.sh
RUN apk add gcc && strip /tmp/naive
COPY --from=caddy /tmp/caddy /tmp/

# Compile open-snell
FROM golang:1.17-alpine3.16 AS snell
ENV SNELL_VERSION="v3.0.1"
RUN \
  wget https://github.com/icpz/open-snell/archive/refs/tags/${SNELL_VERSION}.tar.gz && \
  tar xf ${SNELL_VERSION}.tar.gz && cd ./open-snell-*/ && \
  env CGO_ENABLED=0 go build -trimpath \
    -ldflags "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL_VERSION}'" ./cmd/snell-client && \
  env CGO_ENABLED=0 go build -trimpath \
    -ldflags "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL_VERSION}'" ./cmd/snell-server && \
  mv ./snell-client ./snell-server /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/snell-*

# Compile hysteria
FROM golang:1.17-alpine3.16 AS hysteria
ENV HYSTERIA_VERSION="v1.1.0"
RUN \
  apk add git && \
  git clone https://github.com/HyNetwork/hysteria.git && \
  cd ./hysteria/ && git checkout ${HYSTERIA_VERSION} && cd ./cmd/ && \
  env CGO_ENABLED=0 go build -o hysteria -trimpath -ldflags "-s -w \
    -X 'main.appVersion=$(git describe --tags)' \
    -X 'main.appCommit=$(git rev-parse HEAD)' \
    -X 'main.appDate=$(date "+%F %T")'" && \
  mv ./hysteria /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/hysteria

# Compile relaybaton
FROM golang:1.14-alpine3.13 AS relaybaton
ENV RELAYBATON_VERSION="v0.6.0"
RUN \
  apk add build-base git perl rsync && \
  wget https://github.com/iyouport-org/relaybaton/archive/refs/tags/${RELAYBATON_VERSION}.tar.gz
RUN \
  tar xf ${RELAYBATON_VERSION}.tar.gz && cd ./relaybaton-*/ && \
  make && mv ./bin/relaybaton /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/relaybaton

# Compile pingtunnel
FROM golang:1.18-alpine3.16 AS pingtunnel
RUN \
  apk add git && \
  git clone https://github.com/esrrhs/pingtunnel.git && cd ./pingtunnel/ && \
  env GO111MODULE=off go get github.com/esrrhs/pingtunnel/... && \
  env GO111MODULE=off CGO_ENABLED=0 go build -ldflags="-s -w" && \
  mv ./pingtunnel /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/pingtunnel

# Compile wireproxy
FROM golang:1.17-alpine3.16 AS wireproxy
ENV WIREPROXY_VERSION="v1.0.3"
RUN \
  wget https://github.com/octeep/wireproxy/archive/refs/tags/${WIREPROXY_VERSION}.tar.gz && \
  tar xf ${WIREPROXY_VERSION}.tar.gz && cd ./wireproxy-*/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" ./cmd/wireproxy && \
  mv ./wireproxy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/wireproxy

# Compile dnsproxy
FROM golang:1.18-alpine3.16 AS dnsproxy
ENV DNSPROXY_VERSION="v0.43.1"
RUN \
  wget https://github.com/AdguardTeam/dnsproxy/archive/refs/tags/${DNSPROXY_VERSION}.tar.gz && \
  tar xf ${DNSPROXY_VERSION}.tar.gz && cd ./dnsproxy-*/ && \
  env CGO_ENABLED=0 go build -trimpath -ldflags "-X main.VersionString=${DNSPROXY_VERSION} -s -w" && \
  mv ./dnsproxy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/dnsproxy

# Combine all release
FROM python:3.10-alpine3.16 AS asset
COPY --from=python-pkg /packages.tar.gz /
RUN \
  PACKAGE_DIR="/asset/usr/local/lib/$(ls /usr/local/lib/ | grep ^python)" && \
  mkdir -p ${PACKAGE_DIR}/ && tar xf /packages.tar.gz -C ${PACKAGE_DIR}/
COPY --from=openssl /tmp/libcrypto.so* /asset/lib/
COPY --from=shadowsocks /release/ /asset/usr/bin/
COPY --from=plugin /release/ /asset/usr/bin/
COPY --from=v2ray /tmp/v2* /asset/usr/bin/
COPY --from=xray /tmp/xray /asset/usr/bin/
COPY --from=trojan /tmp/trojan* /asset/usr/bin/
COPY --from=gost /tmp/gost* /asset/usr/bin/
COPY --from=brook /tmp/brook /asset/usr/bin/
COPY --from=clash /tmp/clash /asset/usr/bin/
COPY --from=snell /tmp/snell-* /asset/usr/bin/
COPY --from=hysteria /tmp/hysteria /asset/usr/bin/
COPY --from=naiveproxy /tmp/caddy /asset/usr/bin/
COPY --from=naiveproxy /tmp/naive /asset/usr/bin/
COPY --from=relaybaton /tmp/relaybaton /asset/usr/bin/
COPY --from=pingtunnel /tmp/pingtunnel /asset/usr/bin/
COPY --from=wireproxy /tmp/wireproxy /asset/usr/bin/
COPY --from=dnsproxy /tmp/dnsproxy /asset/usr/bin/

# Release docker image
FROM python:3.10-alpine3.16
RUN \
  apk add --no-cache boost-program_options c-ares glib libev libsodium libstdc++ mbedtls pcre && \
  pip3 --no-cache-dir install colorlog pysocks requests
COPY --from=asset /asset /
