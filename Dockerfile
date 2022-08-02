ARG ALPINE="alpine:3.16"
ARG PYTHON="python:3.10-alpine3.16"
ARG RUST="rust:1.62-alpine3.16"
ARG GO18="golang:1.18-alpine3.16"
ARG GO17="golang:1.17-alpine3.16"
ARG GO16="golang:1.16-alpine3.15"

# Compile upx (can't use gcc11 for now)
FROM alpine:3.15 AS upx
ENV UPX_VERSION="3.96"
RUN apk add bash build-base perl ucl-dev zlib-dev
RUN wget https://github.com/upx/upx/releases/download/v${UPX_VERSION}/upx-${UPX_VERSION}-src.tar.xz
RUN tar xf upx-${UPX_VERSION}-src.tar.xz
WORKDIR ./upx-${UPX_VERSION}-src/
RUN make all && mv ./src/upx.out /usr/bin/upx
RUN mkdir -p /upx/lib/ && mkdir -p /upx/bin/
RUN cp -d /usr/lib/libgcc_s.so* /usr/lib/libstdc++.so* /usr/lib/libucl.so* /upx/lib/
RUN cp /usr/bin/upx /upx/bin/

# Download build-base
FROM ${ALPINE} AS build-base
WORKDIR /apk/
RUN apk add build-base | grep -oE 'Installing \S+' | cut -b 12- > build-base && chmod +x build-base
RUN cat ./build-base | xargs -n1 apk fetch
RUN sed -i 's/^/apk add \/apk\/&/g;s/$/&-*.apk/g;1i\#!/bin/sh' ./build-base

# Compile gevent
FROM ${PYTHON} AS gevent
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && apk add libffi-dev
RUN cd /tmp/ && pip wheel gevent

# Compile numpy
FROM ${PYTHON} AS numpy
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base
RUN cd /tmp/ && pip wheel numpy

# Build python wheels
FROM ${PYTHON} AS wheels
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && apk add linux-headers
RUN cd /tmp/ && pip wheel colorlog flask IPy psutil pysocks requests salsa20
COPY --from=gevent /tmp/*.whl /tmp/
COPY --from=numpy /tmp/*.whl /tmp/

# Compile shadowsocks-rust
FROM ${RUST} AS ss-rust
COPY --from=build-base /apk/ /apk/
ENV SS_RUST="v1.15.0-alpha.8"
RUN /apk/build-base
RUN wget https://github.com/shadowsocks/shadowsocks-rust/archive/refs/tags/${SS_RUST}.tar.gz
RUN tar xf ${SS_RUST}.tar.gz && mv ./shadowsocks-rust-*/ ./shadowsocks-rust/
WORKDIR ./shadowsocks-rust/
RUN cargo update
RUN cargo build --release --bin sslocal --bin ssserver \
      --features "stream-cipher aead-cipher-extra aead-cipher-2022 aead-cipher-2022-extra"
RUN cd ./target/release/ && mv ./sslocal /tmp/ss-rust-local && mv ./ssserver /tmp/ss-rust-server
RUN strip /tmp/ss-rust-*
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/ss-rust-*

# Compile shadowsocks-libev
FROM ${ALPINE} AS ss-libev
COPY --from=build-base /apk/ /apk/
ENV SS_LIBEV="3.3.5"
RUN /apk/build-base
RUN apk add c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev
RUN wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v${SS_LIBEV}/shadowsocks-libev-${SS_LIBEV}.tar.gz
RUN tar xf shadowsocks-libev-*.tar.gz && mv ./shadowsocks-libev-*/ ./shadowsocks-libev/
WORKDIR ./shadowsocks-libev/
RUN ./configure --disable-documentation && make
RUN mv ./src/ss-local /tmp/ss-libev-local && mv ./src/ss-server /tmp/ss-libev-server
RUN strip /tmp/ss-libev-*

# Package shadowsocks-python (lastest version, legacy version, R version aka ssr)
FROM ${PYTHON} AS ss-python
ENV SS_PYTHON_LEGACY="2.6.2"
RUN apk add git && mkdir /packages/
RUN git clone https://github.com/dnomd343/shadowsocksr.git
RUN git clone https://github.com/shadowsocks/shadowsocks.git
RUN wget https://github.com/shadowsocks/shadowsocks/archive/refs/tags/${SS_PYTHON_LEGACY}.tar.gz
RUN tar xf ${SS_PYTHON_LEGACY}.tar.gz
# shadowsocks-python (R version)
WORKDIR ./shadowsocksr/
RUN sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/ordereddict.py && \
    sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
    sed -i "/for path in paths:/a\        if 'libcrypto.so' in path:" ./shadowsocks/crypto/util.py && \
    sed -i "/libcrypto.so/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py
RUN python3 setup.py build && cd ./build/lib/shadowsocks/ && \
    chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
    mv ../../lib/ /packages/ssr-python/
# shadowsocks-python (latest version)
WORKDIR ../shadowsocks/
RUN git checkout master
RUN sed -i 's/if addr is/if addr ==/g' ./shadowsocks/common.py && \
    sed -i 's/and ip is not/and ip !=/g' ./shadowsocks/common.py && \
    sed -i 's/if len(block) is/if len(block) ==/g' ./shadowsocks/common.py && \
    sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py
RUN python3 setup.py build && cd ./build/lib/shadowsocks/ && \
    chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
    mv ../../lib/ /packages/ss-python/
# shadowsocks-python (legacy version)
WORKDIR ../shadowsocks-${SS_PYTHON_LEGACY}/
RUN sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    sed -i "s/find_library(p)/'libsodium.so.23'/g" ./shadowsocks/crypto/ctypes_libsodium.py && \
    sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py
RUN python3 setup.py build && cd ./build/lib/shadowsocks/ && \
    chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
    mv ../../lib/ /packages/ss-python-legacy/

# Compile shadowsocks-bootstrap
FROM ${ALPINE} AS ss-bootstrap
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && apk add cmake git glib-dev
RUN git clone https://github.com/dnomd343/shadowsocks-bootstrap.git
WORKDIR ./shadowsocks-bootstrap/build/
RUN cmake -DCMAKE_BUILD_TYPE=Release .. && make
RUN mv ../bin/ss-bootstrap-* /tmp/
RUN strip /tmp/ss-bootstrap-*

# Combine shadowsocks dependencies
FROM ${PYTHON} AS shadowsocks
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

# Pack python modules
FROM ${ALPINE} AS python-pkg
COPY --from=wheels /tmp/*.whl /site-packages/
RUN cd /site-packages/ && ls | xargs -n1 unzip && rm ./*.whl
COPY --from=ss-python /packages/ /site-packages/
RUN rm -rf $(find / -name '__pycache__')
RUN BZIP2=-9 tar czf /packages.tar.gz ./site-packages/

# Compile openssl (old version, for shadowsocks method -> idea-cfb / seed-cfb)
FROM ${ALPINE} AS openssl
COPY --from=build-base /apk/ /apk/
ENV OPENSSL_VER="1.0.2"
ENV OPENSSL_SUB_VER="u"
RUN /apk/build-base && apk add perl
RUN wget https://www.openssl.org/source/old/${OPENSSL_VER}/openssl-${OPENSSL_VER}${OPENSSL_SUB_VER}.tar.gz
RUN tar xf openssl-*.tar.gz && mv ./openssl-*/ ./openssl/
WORKDIR ./openssl/
RUN ./config --shared --prefix=/usr && make
RUN mv ./libcrypto.so.1.0.0 /tmp/
RUN strip /tmp/libcrypto.so.1.0.0

# Compile sip003 plugins (part1 -> gcc & cargo)
FROM ${RUST} AS plugin-1
COPY --from=build-base /apk/ /apk/
RUN apk add git && mkdir /plugins/
RUN /apk/build-base && apk add autoconf automake libev-dev libtool linux-headers
RUN git clone https://github.com/shadowsocks/simple-obfs.git
RUN git clone https://github.com/shadowsocks/qtun.git
# Compile simple-obfs
WORKDIR ./simple-obfs/
RUN git submodule update --init --recursive
RUN ./autogen.sh && ./configure --disable-documentation && make
RUN cd ./src/ && mv ./obfs-local ./obfs-server /plugins/
# Compile qtun
WORKDIR ../qtun/
RUN cargo update
RUN cargo build --release
RUN cd ./target/release/ && mv ./qtun-client ./qtun-server /plugins/
RUN strip /plugins/*
COPY --from=upx /upx/ /usr/
RUN upx -9 /plugins/qtun-*

# Compile sip003 plugins (part2 -> go1.16)
FROM ${GO16} AS plugin-2
ENV GOST_PLUGIN="v1.6.3"
RUN apk add git && mkdir /plugins/
RUN git clone https://github.com/Qv2ray/gun.git
RUN git clone https://github.com/dnomd343/kcptun.git
RUN git clone https://github.com/dnomd343/GoQuiet.git
RUN git clone https://github.com/ihciah/rabbit-tcp.git
RUN git clone https://github.com/dnomd343/rabbit-plugin.git
RUN git clone https://github.com/maskedeken/gost-plugin.git
RUN git clone https://github.com/shadowsocks/v2ray-plugin.git
RUN git clone https://github.com/IrineSistiana/mos-tls-tunnel.git
# Compile v2ray-plugin
WORKDIR ./v2ray-plugin/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w"
RUN mv ./v2ray-plugin /plugins/
# Compile kcptun
WORKDIR ../kcptun/
RUN git checkout sip003
RUN go mod init github.com/shadowsocks/kcptun && go mod tidy
RUN env CGO_ENABLED=0 go build -v -o kcptun-client -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./client
RUN env CGO_ENABLED=0 go build -v -o kcptun-server -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./server
RUN mv ./kcptun-client ./kcptun-server /plugins/
# Compile gost-plugin
WORKDIR ../gost-plugin/
RUN git checkout ${GOST_PLUGIN} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w"
RUN mv ./gost-plugin /plugins/
# Compile GoQuiet
WORKDIR ../GoQuiet/
RUN go mod init github.com/cbeuw/GoQuiet
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-client
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-server
RUN mv ./gq-client ./gq-server /plugins/
# Compile mos-tls-tunnel
WORKDIR ../mos-tls-tunnel/
RUN go mod init github.com/IrineSistiana/mos-tls-tunnel && go mod vendor
RUN env CGO_ENABLED=0 go build -v -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-client
RUN env CGO_ENABLED=0 go build -v -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-server
RUN mv ./mtt-client ./mtt-server /plugins/
# Compile rabbit-plugin
WORKDIR ../rabbit-plugin/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w"
RUN mv ./rabbit-plugin /plugins/
# Compile rabbit-tcp
WORKDIR ../rabbit-tcp/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.Version=$(git describe --tags) -s -w" ./cmd/rabbit.go
RUN mv ./rabbit /plugins/
# Compile gun-plugin
WORKDIR ../gun/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -o gun-plugin -trimpath -ldflags "-s -w" ./cmd/sip003/
RUN mv ./gun-plugin /plugins/
COPY --from=upx /upx/ /usr/
RUN upx -9 /plugins/*

# Compile sip003 plugins (part3 -> go1.17)
FROM ${GO17} AS plugin-3
ENV SIMPLE_TLS="v0.7.0"
ENV CLOAK="v2.6.0"
RUN apk add git && mkdir /plugins/
RUN git clone https://github.com/cbeuw/Cloak.git
RUN git clone https://github.com/teddysun/xray-plugin.git
RUN git clone https://github.com/IrineSistiana/simple-tls.git
# Compile simple-tls
WORKDIR ./simple-tls/
RUN git checkout ${SIMPLE_TLS} && go mod download -x
RUN sed -i 's/version = "unknown\/dev"/version = "'$(git describe --tags)'"/g' main.go
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w"
RUN mv ./simple-tls /plugins/
# Compile xray-plugin
WORKDIR ../xray-plugin/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w"
RUN mv ./xray-plugin /plugins/
# Compile Cloak
WORKDIR ../Cloak/
RUN git checkout ${CLOAK} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-client
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-server
RUN mv ./ck-client ./ck-server /plugins/
COPY --from=upx /upx/ /usr/
RUN upx -9 /plugins/*

# Combine sip003 plugins
FROM ${ALPINE} AS plugin
COPY --from=plugin-1 /plugins/ /release/
COPY --from=plugin-2 /plugins/ /release/
COPY --from=plugin-3 /plugins/ /release/

# Compile v2fly-core
FROM ${GO18} AS v2ray
ENV V2RAY_VERSION="v4.45.2"
RUN wget https://github.com/v2fly/v2ray-core/archive/refs/tags/${V2RAY_VERSION}.tar.gz
RUN tar xf ${V2RAY_VERSION}.tar.gz && mv ./v2ray-core-*/ ./v2ray-core/
WORKDIR ./v2ray-core/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -o v2ray -trimpath -ldflags "-s -w" ./main
RUN env CGO_ENABLED=0 go build -v -o v2ctl -trimpath -ldflags "-s -w" -tags confonly ./infra/control/main
RUN mv ./v2ctl ./v2ray /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/v2*

# Compile xray-core
FROM ${GO18} AS xray
ENV XRAY_VERSION="v1.5.9"
RUN wget https://github.com/XTLS/Xray-core/archive/refs/tags/${XRAY_VERSION}.tar.gz
RUN tar xf ${XRAY_VERSION}.tar.gz && mv ./Xray-core-*/ ./Xray-core/
WORKDIR ./Xray-core/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -o xray -trimpath -ldflags "-s -w" ./main
RUN mv ./xray /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/xray

# Compile trojan-go
FROM ${GO17} AS trojan-go
ENV TROJAN_GO_VERSION="v0.10.6"
RUN apk add git
RUN git clone https://github.com/p4gefau1t/trojan-go.git
WORKDIR ./trojan-go/
RUN git checkout ${TROJAN_GO_VERSION} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags " \
      -X github.com/p4gefau1t/trojan-go/constant.Version=$(git describe --dirty) \
      -X github.com/p4gefau1t/trojan-go/constant.Commit=$(git rev-parse HEAD) -s -w" -tags "full"
RUN mv ./trojan-go /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/trojan-go

# Compile trojan
FROM ${ALPINE} AS trojan
COPY --from=build-base /apk/ /apk/
ENV TROJAN_VERSION="v1.16.0"
RUN /apk/build-base && apk add boost-dev cmake openssl-dev
RUN wget https://github.com/trojan-gfw/trojan/archive/refs/tags/${TROJAN_VERSION}.tar.gz
RUN tar xf ${TROJAN_VERSION}.tar.gz && mv ./trojan-*/ ./trojan/
WORKDIR ./trojan/build/
RUN cmake .. -DENABLE_MYSQL=OFF -DSYSTEMD_SERVICE=OFF && make
RUN mv ./trojan /tmp/
RUN strip /tmp/trojan
COPY --from=trojan-go /tmp/trojan-go /tmp/

# Compile gost-v3
FROM ${GO18} AS gost-v3
RUN apk add git
RUN git clone https://github.com/go-gost/gost.git
WORKDIR ./gost/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/gost
RUN mv ./gost /tmp/gost-v3
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/gost-v3

# Compile gost
FROM ${GO17} AS gost
ENV GOST_VERSION="v2.11.2"
RUN wget https://github.com/ginuerzh/gost/archive/refs/tags/${GOST_VERSION}.tar.gz
RUN tar xf ${GOST_VERSION}.tar.gz && mv ./gost-*/ ./gost/
WORKDIR ./gost/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/gost
RUN mv ./gost /tmp/
COPY --from=gost-v3 /tmp/gost-v3 /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/gost

# Compile brook
FROM ${GO16} AS brook
ENV BROOK_VERSION="v20220707"
RUN wget https://github.com/txthinking/brook/archive/refs/tags/${BROOK_VERSION}.tar.gz
RUN tar xf ${BROOK_VERSION}.tar.gz && mv ./brook-*/ ./brook/
WORKDIR ./brook/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cli/brook
RUN mv ./brook /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/brook

# Compile clash
FROM ${GO18} AS clash
ENV CLASH_VERSION="v1.11.4"
RUN wget https://github.com/Dreamacro/clash/archive/refs/tags/${CLASH_VERSION}.tar.gz
RUN tar xf ${CLASH_VERSION}.tar.gz && mv ./clash-*/ ./clash/
WORKDIR ./clash/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w \
      -X 'github.com/Dreamacro/clash/constant.Version=${CLASH_VERSION}' \
      -X 'github.com/Dreamacro/clash/constant.BuildTime=$(date -u)'"
RUN mv ./clash /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/clash

# Compile caddy
FROM ${GO18} AS caddy
RUN go install github.com/caddyserver/xcaddy/cmd/xcaddy@latest
RUN xcaddy build --with github.com/caddyserver/forwardproxy@caddy2=github.com/klzgrad/forwardproxy@naive
RUN mv ./caddy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/caddy

# Download naiveproxy
FROM ${ALPINE} AS naiveproxy
ENV NAIVE_VERSION="v103.0.5060.53-3"
RUN apk add curl libgcc jq
RUN curl -sL https://api.github.com/repos/klzgrad/naiveproxy/releases/tags/${NAIVE_VERSION} \
      | jq .assets | jq .[].name | grep naiveproxy-${NAIVE_VERSION}-openwrt-$(uname -m) \
      | cut -b 2- | rev | cut -b 2- | rev | tac > list.dat
RUN echo -e "while read FILE_NAME;do\nwget https://github.com/klzgrad/naiveproxy/releases/download/\${NAIVE_VERSION}/\${FILE_NAME}\n \
      tar xf \${FILE_NAME} && ldd ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive\n \
      [ \$? -eq 0 ] && cp ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive /tmp/ && break\ndone < list.dat" > naiveproxy.sh
RUN sh naiveproxy.sh
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && strip /tmp/naive
COPY --from=caddy /tmp/caddy /tmp/

# Compile open-snell
FROM ${GO17} AS snell
ENV SNELL_VERSION="v3.0.1"
RUN wget https://github.com/icpz/open-snell/archive/refs/tags/${SNELL_VERSION}.tar.gz
RUN tar xf ${SNELL_VERSION}.tar.gz && mv ./open-snell-*/ ./open-snell/
WORKDIR ./open-snell/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags \
      "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL_VERSION}'" ./cmd/snell-client
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags \
      "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL_VERSION}'" ./cmd/snell-server
RUN mv ./snell-client ./snell-server /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/snell-*

# Compile hysteria
FROM ${GO17} AS hysteria
ENV HYSTERIA_VERSION="v1.1.0"
RUN apk add git
RUN git clone https://github.com/HyNetwork/hysteria.git
WORKDIR ./hysteria/
RUN git checkout ${HYSTERIA_VERSION} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -o hysteria -trimpath -ldflags "-s -w \
      -X 'main.appVersion=$(git describe --tags)' \
      -X 'main.appCommit=$(git rev-parse HEAD)' \
      -X 'main.appDate=$(date "+%F %T")'" ./cmd
RUN mv ./hysteria /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/hysteria

# Compile relaybaton
FROM golang:1.14-alpine3.13 AS relaybaton
ENV RELAYBATON_VERSION="v0.6.0"
RUN apk add build-base git perl rsync
RUN wget https://github.com/iyouport-org/relaybaton/archive/refs/tags/${RELAYBATON_VERSION}.tar.gz
RUN tar xf ${RELAYBATON_VERSION}.tar.gz && cd ./relaybaton-*/ && go mod download -x
RUN cd ./relaybaton-*/ && make && mv ./bin/relaybaton /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/relaybaton

# Compile pingtunnel
FROM ${GO18} AS pingtunnel
RUN apk add git
RUN git clone https://github.com/esrrhs/pingtunnel.git
RUN env GO111MODULE=off go get -v github.com/esrrhs/pingtunnel/...
WORKDIR ./pingtunnel/
RUN env GO111MODULE=off CGO_ENABLED=0 go build -v -ldflags="-s -w"
RUN mv ./pingtunnel /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/pingtunnel

# Compile wireproxy
FROM ${GO17} AS wireproxy
ENV WIREPROXY_VERSION="v1.0.3"
RUN wget https://github.com/octeep/wireproxy/archive/refs/tags/${WIREPROXY_VERSION}.tar.gz
RUN tar xf ${WIREPROXY_VERSION}.tar.gz && mv ./wireproxy-*/ ./wireproxy/
WORKDIR ./wireproxy/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/wireproxy
RUN mv ./wireproxy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/wireproxy

# Compile dnsproxy
FROM ${GO18} AS dnsproxy
ENV DNSPROXY_VERSION="v0.43.1"
RUN wget https://github.com/AdguardTeam/dnsproxy/archive/refs/tags/${DNSPROXY_VERSION}.tar.gz
RUN tar xf ${DNSPROXY_VERSION}.tar.gz && mv ./dnsproxy-*/ ./dnsproxy/
WORKDIR ./dnsproxy/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VersionString=${DNSPROXY_VERSION} -s -w"
RUN mv ./dnsproxy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/dnsproxy

# Compile mad
FROM ${GO16} AS mad
ENV MAD_VERSION="v20210401"
RUN wget https://github.com/txthinking/mad/archive/refs/tags/${MAD_VERSION}.tar.gz
RUN tar xf ${MAD_VERSION}.tar.gz && mv ./mad-*/ ./mad/
WORKDIR ./mad/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -ldflags="-s -w" ./cli/mad
RUN mv ./mad /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/mad

# Combine all release
FROM ${PYTHON} AS asset
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
COPY --from=mad /tmp/mad /asset/usr/bin/

# Release docker image
FROM ${PYTHON}
RUN apk add --no-cache boost-program_options c-ares \
      ca-certificates glib libev libsodium libstdc++ mbedtls pcre && \
    ln -s /usr/local/share/ProxyC/main.py /usr/bin/proxyc
COPY --from=asset /asset /
COPY . /usr/local/share/ProxyC/
EXPOSE 7839
CMD ["proxyc"]
