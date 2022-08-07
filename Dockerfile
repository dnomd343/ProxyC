ARG ALPINE_IMG="alpine:3.16"
ARG RUST_IMG="rust:1.62-alpine3.16"
ARG GO14_IMG="golang:1.14-alpine3.13"
ARG GO16_IMG="golang:1.16-alpine3.15"
ARG GO17_IMG="golang:1.17-alpine3.16"
ARG GO18_IMG="golang:1.18-alpine3.16"
ARG PYTHON_IMG="python:3.10-alpine3.16"

# Download build-base
FROM ${ALPINE_IMG} AS build-base
WORKDIR /apk/
RUN apk add build-base | grep -oE 'Installing \S+' | cut -b 12- > ./build-base
RUN chmod +x ./build-base && cat ./build-base | xargs -n1 apk fetch && \
    sed -i 's/^/ \/apk\/&/g;s/$/&-*.apk/g;1i\apk add' ./build-base && sed -i ':a;N;s/\n//g;ba' ./build-base

# Compile numpy
FROM ${PYTHON_IMG} AS numpy
WORKDIR /wheels/
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && pip wheel numpy

# Compile gevent
FROM ${PYTHON_IMG} AS gevent
WORKDIR /wheels/
RUN apk add libffi-dev
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && pip wheel gevent

# Build python wheels
FROM ${PYTHON_IMG} AS wheels
WORKDIR /wheels/
RUN apk add linux-headers
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && pip wheel colorlog flask IPy psutil pysocks pyyaml requests salsa20
COPY --from=gevent /wheels/*.whl /wheels/
COPY --from=numpy /wheels/*.whl /wheels/

# Compile upx (under gcc10)
FROM ${ALPINE_IMG} AS upx
ENV UPX_VERSION="3.96"
RUN sed -i 's/v3.\d\d/v3.15/' /etc/apk/repositories && \
    apk add bash build-base perl ucl-dev zlib-dev
RUN wget https://github.com/upx/upx/releases/download/v${UPX_VERSION}/upx-${UPX_VERSION}-src.tar.xz && \
    tar xf upx-${UPX_VERSION}-src.tar.xz
WORKDIR ./upx-${UPX_VERSION}-src/
RUN make -C ./src/ && mkdir -p /upx/bin/ && mv ./src/upx.out /upx/bin/upx && \
    mkdir -p /upx/lib/ && cd /usr/lib/ && cp -d ./libgcc_s.so* ./libstdc++.so* ./libucl.so* /upx/lib/

# Compile shadowsocks-rust
FROM ${RUST_IMG} AS ss-rust
ENV SS_RUST="1.15.0-alpha.8"
COPY --from=build-base /apk/ /apk/
RUN wget https://github.com/shadowsocks/shadowsocks-rust/archive/refs/tags/v${SS_RUST}.tar.gz && \
    tar xf v${SS_RUST}.tar.gz && /apk/build-base
WORKDIR ./shadowsocks-rust-${SS_RUST}/
RUN cargo update
RUN cargo build --target-dir ./ --release --bin sslocal --bin ssserver \
      --features "stream-cipher aead-cipher-extra aead-cipher-2022 aead-cipher-2022-extra" && \
    mv ./release/sslocal /tmp/ss-rust-local && mv ./release/ssserver /tmp/ss-rust-server && \
    strip /tmp/ss-rust-*
COPY --from=upx /upx/ /usr/
RUN ls /tmp/ss-rust-* | xargs -P0 -n1 upx -9

# Compile shadowsocks-libev
FROM ${ALPINE_IMG} AS ss-libev
ENV SS_LIBEV="3.3.5"
RUN apk add c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev
COPY --from=build-base /apk/ /apk/
RUN wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v${SS_LIBEV}/shadowsocks-libev-${SS_LIBEV}.tar.gz && \
    tar xf shadowsocks-libev-*.tar.gz && /apk/build-base
WORKDIR ./shadowsocks-libev-${SS_LIBEV}/
RUN ./configure --disable-documentation && make && \
    mv ./src/ss-local /tmp/ss-libev-local && mv ./src/ss-server /tmp/ss-libev-server && \
    strip /tmp/ss-libev-*

# Package shadowsocks-python (lastest version, legacy version, R version aka ssr)
FROM ${PYTHON_IMG} AS ss-python
ENV SS_PYTHON_LEGACY="2.6.2"
RUN apk add git && mkdir /packages/ && \
    git clone https://github.com/dnomd343/shadowsocksr.git && \
    git clone https://github.com/shadowsocks/shadowsocks.git && \
    wget https://github.com/shadowsocks/shadowsocks/archive/refs/tags/${SS_PYTHON_LEGACY}.tar.gz && \
    tar xf ${SS_PYTHON_LEGACY}.tar.gz
# shadowsocks-python (R version)
WORKDIR ./shadowsocksr/
RUN sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/ordereddict.py && \
    sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
    sed -i "/for path in paths:/a\        if 'libcrypto.so' in path:" ./shadowsocks/crypto/util.py && \
    sed -i "/libcrypto.so/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py && \
    python3 setup.py build && cd ./build/lib/shadowsocks/ && \
    chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
    mv ../../lib/ /packages/ssr-python/
# shadowsocks-python (latest version)
WORKDIR ../shadowsocks/
RUN git checkout master && \
    sed -i 's/if addr is/if addr ==/g' ./shadowsocks/common.py && \
    sed -i 's/and ip is not/and ip !=/g' ./shadowsocks/common.py && \
    sed -i 's/if len(block) is/if len(block) ==/g' ./shadowsocks/common.py && \
    sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    python3 setup.py build && cd ./build/lib/shadowsocks/ && \
    chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
    mv ../../lib/ /packages/ss-python/
# shadowsocks-python (legacy version)
WORKDIR ../shadowsocks-${SS_PYTHON_LEGACY}/
RUN sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    sed -i "s/find_library(p)/'libsodium.so.23'/g" ./shadowsocks/crypto/ctypes_libsodium.py && \
    sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
    python3 setup.py build && cd ./build/lib/shadowsocks/ && \
    chmod +x ./local.py ./server.py && mv ./local.py ./server.py ../ && \
    mv ../../lib/ /packages/ss-python-legacy/

# Compile shadowsocks-bootstrap
FROM ${ALPINE_IMG} AS ss-bootstrap
RUN apk add cmake git glib-dev
COPY --from=build-base /apk/ /apk/
RUN git clone https://github.com/dnomd343/shadowsocks-bootstrap.git && /apk/build-base
WORKDIR ./shadowsocks-bootstrap/build/
RUN cmake -DCMAKE_BUILD_TYPE=Release .. && make && \
    mv ../bin/ss-bootstrap-* /tmp/ && \
    strip /tmp/ss-bootstrap-*

# Combine shadowsocks dependencies
FROM ${PYTHON_IMG} AS shadowsocks
COPY --from=ss-rust /tmp/ss-rust-* /release/
COPY --from=ss-libev /tmp/ss-libev-* /release/
COPY --from=ss-bootstrap /tmp/ss-bootstrap-* /release/
ARG PYTHON="3.10"
RUN ln -s /usr/local/lib/python${PYTHON}/site-packages/ssr-python/local.py /release/ssr-local && \
    ln -s /usr/local/lib/python${PYTHON}/site-packages/ssr-python/server.py /release/ssr-server && \
    ln -s /usr/local/lib/python${PYTHON}/site-packages/ss-python/local.py /release/ss-python-local && \
    ln -s /usr/local/lib/python${PYTHON}/site-packages/ss-python/server.py /release/ss-python-server && \
    ln -s /usr/local/lib/python${PYTHON}/site-packages/ss-python-legacy/local.py /release/ss-python-legacy-local && \
    ln -s /usr/local/lib/python${PYTHON}/site-packages/ss-python-legacy/server.py /release/ss-python-legacy-server

# Pack python modules
FROM ${ALPINE_IMG} AS python-pkg
COPY --from=wheels /wheels/*.whl /site-packages/
COPY --from=ss-python /packages/ /site-packages/
WORKDIR /site-packages/
RUN ls ./*.whl | xargs -n1 unzip && rm ./*.whl && \
    rm -rf $(find ./ -name '__pycache__') && \
    BZIP2=-9 tar czf /packages.tar.gz ./

# Compile openssl (old version, for shadowsocks method -> idea-cfb / seed-cfb)
FROM ${ALPINE_IMG} AS openssl
ENV OPENSSL_VER="1.0.2"
ENV OPENSSL_SUB_VER="u"
RUN apk add perl
COPY --from=build-base /apk/ /apk/
RUN wget https://www.openssl.org/source/old/${OPENSSL_VER}/openssl-${OPENSSL_VER}${OPENSSL_SUB_VER}.tar.gz && \
    tar xf openssl-*.tar.gz && /apk/build-base
WORKDIR ./openssl-${OPENSSL_VER}${OPENSSL_SUB_VER}/
RUN ./config --shared --prefix=/usr && make && \
    mv ./libcrypto.so.1.0.0 /tmp/ && \
    strip /tmp/libcrypto.so.1.0.0

# Compile sip003 plugins (part1 -> gcc & cargo)
FROM ${RUST_IMG} AS plugin-1
RUN apk add autoconf automake git libev-dev libtool linux-headers
COPY --from=build-base /apk/ /apk/
RUN git clone https://github.com/shadowsocks/qtun.git && \
    git clone https://github.com/shadowsocks/simple-obfs.git && \
    /apk/build-base && mkdir -p /plugins/
# Compile simple-obfs
WORKDIR ./simple-obfs/
RUN git submodule update --init --recursive && \
    ./autogen.sh && ./configure --disable-documentation && make && \
    mv ./src/obfs-local ./src/obfs-server /plugins/
# Compile qtun
WORKDIR ../qtun/
RUN cargo update
RUN cargo build --target-dir ./ --release && \
    mv ./release/qtun-client ./release/qtun-server /plugins/ && \
    strip /plugins/*
COPY --from=upx /upx/ /usr/
RUN ls /plugins/qtun-* | xargs -P0 -n1 upx -9

# Compile sip003 plugins (part2 -> go1.16)
FROM ${GO16_IMG} AS plugin-2
ENV GOST_PLUGIN="v1.6.3"
RUN apk add git && mkdir /plugins/
RUN git clone https://github.com/Qv2ray/gun.git && \
    git clone https://github.com/dnomd343/kcptun.git && \
    git clone https://github.com/dnomd343/GoQuiet.git && \
    git clone https://github.com/ihciah/rabbit-tcp.git && \
    git clone https://github.com/dnomd343/rabbit-plugin.git && \
    git clone https://github.com/maskedeken/gost-plugin.git && \
    git clone https://github.com/shadowsocks/v2ray-plugin.git && \
    git clone https://github.com/IrineSistiana/mos-tls-tunnel.git
# Compile v2ray-plugin
WORKDIR ./v2ray-plugin/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
    mv ./v2ray-plugin /plugins/
# Compile kcptun
WORKDIR ../kcptun/
RUN git checkout sip003 && \
    go mod init github.com/shadowsocks/kcptun && go mod tidy
RUN env CGO_ENABLED=0 go build -v -o kcptun-client -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./client && \
    env CGO_ENABLED=0 go build -v -o kcptun-server -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./server && \
    mv ./kcptun-client ./kcptun-server /plugins/
# Compile gost-plugin
WORKDIR ../gost-plugin/
RUN git checkout ${GOST_PLUGIN} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
    mv ./gost-plugin /plugins/
# Compile GoQuiet
WORKDIR ../GoQuiet/
RUN go mod init github.com/cbeuw/GoQuiet
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-client && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-server && \
    mv ./gq-client ./gq-server /plugins/
# Compile mos-tls-tunnel
WORKDIR ../mos-tls-tunnel/
RUN go mod init github.com/IrineSistiana/mos-tls-tunnel && go mod vendor
RUN env CGO_ENABLED=0 go build -v -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-client && \
    env CGO_ENABLED=0 go build -v -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-server && \
    mv ./mtt-client ./mtt-server /plugins/
# Compile rabbit-plugin
WORKDIR ../rabbit-plugin/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && \
    mv ./rabbit-plugin /plugins/
# Compile rabbit-tcp
WORKDIR ../rabbit-tcp/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.Version=$(git describe --tags) -s -w" ./cmd/rabbit.go && \
    mv ./rabbit /plugins/
# Compile gun-plugin
WORKDIR ../gun/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -o gun-plugin -trimpath -ldflags "-s -w" ./cmd/sip003/ && \
    mv ./gun-plugin /plugins/
COPY --from=upx /upx/ /usr/
RUN ls /plugins/* | xargs -P0 -n1 upx -9

# Compile sip003 plugins (part3 -> go1.17)
FROM ${GO17_IMG} AS plugin-3
ENV SIMPLE_TLS="v0.7.0"
ENV CLOAK="v2.6.0"
RUN apk add git && mkdir /plugins/
RUN git clone https://github.com/cbeuw/Cloak.git && \
    git clone https://github.com/teddysun/xray-plugin.git && \
    git clone https://github.com/IrineSistiana/simple-tls.git
# Compile simple-tls
WORKDIR ./simple-tls/
RUN git checkout ${SIMPLE_TLS} && go mod download -x
RUN sed -i 's/version = "unknown\/dev"/version = "'$(git describe --tags)'"/g' main.go && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && \
    mv ./simple-tls /plugins/
# Compile xray-plugin
WORKDIR ../xray-plugin/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
    mv ./xray-plugin /plugins/
# Compile Cloak
WORKDIR ../Cloak/
RUN git checkout ${CLOAK} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-client && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-server && \
    mv ./ck-client ./ck-server /plugins/
COPY --from=upx /upx/ /usr/
RUN ls /plugins/* | xargs -P0 -n1 upx -9

# Combine sip003 plugins
FROM ${ALPINE_IMG} AS plugin
COPY --from=plugin-1 /plugins/ /plugins/
COPY --from=plugin-2 /plugins/ /plugins/
COPY --from=plugin-3 /plugins/ /plugins/

# Compile xray-core and v2fly-core
FROM ${GO18_IMG} AS v2ray
ENV XRAY_VERSION="1.5.9"
ENV V2FLY_VERSION="4.45.2"
RUN wget https://github.com/XTLS/Xray-core/archive/refs/tags/v${XRAY_VERSION}.tar.gz && \
    tar xf v${XRAY_VERSION}.tar.gz
RUN wget https://github.com/v2fly/v2ray-core/archive/refs/tags/v${V2FLY_VERSION}.tar.gz && \
    tar xf v${V2FLY_VERSION}.tar.gz
WORKDIR ./Xray-core-${XRAY_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -o xray -trimpath -ldflags "-s -w" ./main && \
    mv ./xray /tmp/
WORKDIR ../v2ray-core-${V2FLY_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -o v2ray -trimpath -ldflags "-s -w" ./main && \
    mv ./v2ray /tmp/
COPY --from=upx /upx/ /usr/
RUN ls /tmp/*ray | xargs -P0 -n1 upx -9

# Compile trojan-go
FROM ${GO17_IMG} AS trojan-go
ENV TROJAN_GO_VERSION="v0.10.6"
RUN apk add git
RUN git clone https://github.com/p4gefau1t/trojan-go.git
WORKDIR ./trojan-go/
RUN git checkout ${TROJAN_GO_VERSION} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags " \
      -X github.com/p4gefau1t/trojan-go/constant.Version=$(git describe --dirty) \
      -X github.com/p4gefau1t/trojan-go/constant.Commit=$(git rev-parse HEAD) -s -w" -tags "full" && \
    mv ./trojan-go /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/trojan-go

# Compile trojan
FROM ${ALPINE_IMG} AS trojan
ENV TROJAN_VERSION="1.16.0"
RUN apk add boost-dev cmake openssl-dev
COPY --from=build-base /apk/ /apk/
RUN wget https://github.com/trojan-gfw/trojan/archive/refs/tags/v${TROJAN_VERSION}.tar.gz && \
    tar xf v${TROJAN_VERSION}.tar.gz && /apk/build-base
WORKDIR ./trojan-${TROJAN_VERSION}/build/
RUN cmake .. -DENABLE_MYSQL=OFF -DSYSTEMD_SERVICE=OFF && make && \
    mv ./trojan /tmp/ && \
    strip /tmp/trojan
COPY --from=trojan-go /tmp/trojan-go /tmp/

# Compile gost and gost-v3
FROM ${GO18_IMG} AS gost
ENV GOST_VERSION="2.11.2"
RUN apk add git
RUN git clone https://github.com/go-gost/gost.git ./gost-v3/ && \
    wget https://github.com/ginuerzh/gost/archive/refs/tags/v${GOST_VERSION}.tar.gz && \
    tar xf v${GOST_VERSION}.tar.gz
WORKDIR ./gost-${GOST_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/gost && \
    mv ./gost /tmp/
WORKDIR ../gost-v3/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/gost && \
    mv ./gost /tmp/gost-v3
COPY --from=upx /upx/ /usr/
RUN ls /tmp/gost* | xargs -P0 -n1 upx -9

# Compile brook
FROM ${GO16_IMG} AS brook
ENV BROOK_VERSION="20220707"
RUN wget https://github.com/txthinking/brook/archive/refs/tags/v${BROOK_VERSION}.tar.gz && \
    tar xf v${BROOK_VERSION}.tar.gz
WORKDIR ./brook-${BROOK_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cli/brook && \
    mv ./brook /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/brook

# Compile clash
FROM ${GO18_IMG} AS clash
ENV CLASH_VERSION="1.11.4"
RUN wget https://github.com/Dreamacro/clash/archive/refs/tags/v${CLASH_VERSION}.tar.gz && \
    tar xf v${CLASH_VERSION}.tar.gz
WORKDIR ./clash-${CLASH_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w \
      -X 'github.com/Dreamacro/clash/constant.Version=${CLASH_VERSION}' \
      -X 'github.com/Dreamacro/clash/constant.BuildTime=$(date -u)'" && \
    mv ./clash /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/clash

# Download naiveproxy
FROM ${ALPINE_IMG} AS naiveproxy
ENV NAIVE_VERSION="v103.0.5060.53-3"
RUN apk add curl libgcc jq
RUN curl -sL https://api.github.com/repos/klzgrad/naiveproxy/releases/tags/${NAIVE_VERSION} \
      | jq .assets | jq .[].name | grep naiveproxy-${NAIVE_VERSION}-openwrt-$(uname -m) \
      | cut -b 2- | rev | cut -b 2- | rev | tac > list.dat
RUN echo -e "while read FILE_NAME;do\nwget https://github.com/klzgrad/naiveproxy/releases/download/\${NAIVE_VERSION}/\${FILE_NAME}\n \
      tar xf \${FILE_NAME} && ldd ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive\n \
      [ \$? -eq 0 ] && cp ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive /tmp/ && break\ndone < list.dat" > naiveproxy.sh && \
    sh naiveproxy.sh
COPY --from=build-base /apk/ /apk/
RUN /apk/build-base && strip /tmp/naive

# Compile open-snell
FROM ${GO17_IMG} AS snell
ENV SNELL_VERSION="3.0.1"
RUN wget https://github.com/icpz/open-snell/archive/refs/tags/v${SNELL_VERSION}.tar.gz && \
    tar xf v${SNELL_VERSION}.tar.gz
WORKDIR ./open-snell-${SNELL_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags \
      "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL_VERSION}'" ./cmd/snell-client && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags \
      "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL_VERSION}'" ./cmd/snell-server && \
    mv ./snell-client ./snell-server /tmp/
COPY --from=upx /upx/ /usr/
RUN ls /tmp/snell-* | xargs -P0 -n1 upx -9

# Compile hysteria
FROM ${GO17_IMG} AS hysteria
ENV HYSTERIA_VERSION="v1.1.0"
RUN apk add git
RUN git clone https://github.com/HyNetwork/hysteria.git
WORKDIR ./hysteria/
RUN git checkout ${HYSTERIA_VERSION} && go mod download -x
RUN env CGO_ENABLED=0 go build -v -o hysteria -trimpath -ldflags "-s -w \
      -X 'main.appVersion=$(git describe --tags)' \
      -X 'main.appCommit=$(git rev-parse HEAD)' \
      -X 'main.appDate=$(date "+%F %T")'" ./cmd && \
    mv ./hysteria /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/hysteria

# Compile relaybaton
FROM ${GO14_IMG} AS relaybaton
ENV RELAYBATON_VERSION="0.6.0"
RUN apk add build-base git perl rsync
RUN wget https://github.com/iyouport-org/relaybaton/archive/refs/tags/v${RELAYBATON_VERSION}.tar.gz && \
    tar xf v${RELAYBATON_VERSION}.tar.gz
WORKDIR ./relaybaton-${RELAYBATON_VERSION}/
RUN go mod download -x
RUN make && mv ./bin/relaybaton /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/relaybaton

# Compile pingtunnel
FROM ${GO18_IMG} AS pingtunnel
RUN apk add git
RUN git clone https://github.com/esrrhs/pingtunnel.git
RUN env GO111MODULE=off go get -v github.com/esrrhs/pingtunnel/...
WORKDIR ./pingtunnel/
RUN env GO111MODULE=off CGO_ENABLED=0 go build -v -ldflags="-s -w" && \
    mv ./pingtunnel /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/pingtunnel

# Compile wireproxy
FROM ${GO17_IMG} AS wireproxy
ENV WIREPROXY_VERSION="1.0.3"
RUN wget https://github.com/octeep/wireproxy/archive/refs/tags/v${WIREPROXY_VERSION}.tar.gz && \
    tar xf v${WIREPROXY_VERSION}.tar.gz
WORKDIR ./wireproxy-${WIREPROXY_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/wireproxy && \
    mv ./wireproxy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/wireproxy

# Compile dnsproxy
FROM ${GO18_IMG} AS dnsproxy
ENV DNSPROXY_VERSION="0.43.1"
RUN wget https://github.com/AdguardTeam/dnsproxy/archive/refs/tags/v${DNSPROXY_VERSION}.tar.gz && \
    tar xf v${DNSPROXY_VERSION}.tar.gz
WORKDIR ./dnsproxy-${DNSPROXY_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VersionString=${DNSPROXY_VERSION} -s -w" && \
    mv ./dnsproxy /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/dnsproxy

# Compile mad
FROM ${GO16_IMG} AS mad
ENV MAD_VERSION="20210401"
RUN wget https://github.com/txthinking/mad/archive/refs/tags/v${MAD_VERSION}.tar.gz && \
    tar xf v${MAD_VERSION}.tar.gz
WORKDIR ./mad-${MAD_VERSION}/
RUN go mod download -x
RUN env CGO_ENABLED=0 go build -v -ldflags="-s -w" ./cli/mad && \
    mv ./mad /tmp/
COPY --from=upx /upx/ /usr/
RUN upx -9 /tmp/mad

# Combine all release
FROM ${PYTHON_IMG} AS asset
COPY --from=python-pkg /packages.tar.gz /
ARG PYTHON="3.10"
RUN mkdir -p /asset/usr/local/lib/python${PYTHON}/site-packages/ && \
    tar xf /packages.tar.gz -C /asset/usr/local/lib/python${PYTHON}/site-packages/
COPY --from=openssl /tmp/libcrypto.so* /asset/lib/
COPY --from=shadowsocks /release/ /asset/usr/bin/
COPY --from=plugin /plugins/ /asset/usr/bin/
COPY --from=v2ray /tmp/*ray /asset/usr/bin/
COPY --from=trojan /tmp/trojan* /asset/usr/bin/
COPY --from=gost /tmp/gost* /asset/usr/bin/
COPY --from=brook /tmp/brook /asset/usr/bin/
COPY --from=clash /tmp/clash /asset/usr/bin/
COPY --from=snell /tmp/snell-* /asset/usr/bin/
COPY --from=hysteria /tmp/hysteria /asset/usr/bin/
COPY --from=naiveproxy /tmp/naive /asset/usr/bin/
COPY --from=relaybaton /tmp/relaybaton /asset/usr/bin/
COPY --from=pingtunnel /tmp/pingtunnel /asset/usr/bin/
COPY --from=wireproxy /tmp/wireproxy /asset/usr/bin/
COPY --from=dnsproxy /tmp/dnsproxy /asset/usr/bin/
COPY --from=mad /tmp/mad /asset/usr/bin/
COPY . /asset/usr/local/share/ProxyC/

# Release docker image
FROM ${PYTHON_IMG}
RUN apk add --no-cache boost-program_options c-ares \
      ca-certificates glib libev libsodium libstdc++ mbedtls pcre && \
    ln -s /usr/local/share/ProxyC/main.py /usr/bin/proxyc
COPY --from=asset /asset /
EXPOSE 7839
CMD ["proxyc"]
