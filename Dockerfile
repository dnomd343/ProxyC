ARG ALPINE="alpine:3.16"
ARG RUST="rust:1.64-alpine3.16"
ARG GO14="golang:1.14-alpine3.13"
ARG GO16="golang:1.16-alpine3.15"
ARG GO18="golang:1.18-alpine3.16"
ARG GO19="golang:1.19-alpine3.16"
ARG PYTHON="python:3.10-alpine3.16"

# Download build-base
FROM ${ALPINE} AS build-base
WORKDIR /apk/
RUN echo -e "cd \`dirname \$0\`\napk add --no-network \\" > setup && chmod +x setup && \
    apk update && apk fetch -R build-base cmake | grep -oE '\S+$' | awk '{print "./"$0".apk \\"}' >> setup

# Compile python3 module numpy
FROM ${PYTHON} AS numpy
COPY --from=build-base /apk/ /apk/
WORKDIR /wheels/
RUN /apk/setup && pip wheel numpy

# Compile python3 module gevent
FROM ${PYTHON} AS gevent
RUN apk add libffi-dev
COPY --from=build-base /apk/ /apk/
WORKDIR /wheels/
RUN /apk/setup && pip wheel gevent

# Build python3 wheels
FROM ${PYTHON} AS wheels
RUN apk add linux-headers
COPY --from=build-base /apk/ /apk/
WORKDIR /wheels/
RUN /apk/setup && pip wheel colorlog flask IPy psutil pysocks pyyaml requests salsa20
COPY --from=gevent /wheels/*.whl /wheels/
COPY --from=numpy /wheels/*.whl /wheels/

# Compile upx
FROM ${ALPINE} AS upx
COPY --from=build-base /apk/ /apk/
RUN apk add git && /apk/setup
RUN git clone https://github.com/dnomd343/upx.git
WORKDIR ./upx/
RUN git submodule update --init && rm -rf ./.git/
RUN make UPX_CMAKE_CONFIG_FLAGS=-DCMAKE_EXE_LINKER_FLAGS=-static && \
    mv ./build/release/upx /tmp/ && strip /tmp/upx

# Compile shadowsocks-rust
FROM ${RUST} AS ss-rust
ENV SS_RUST="1.15.0-alpha.8"
COPY --from=build-base /apk/ /apk/
RUN wget https://github.com/shadowsocks/shadowsocks-rust/archive/refs/tags/v${SS_RUST}.tar.gz && \
    tar xf v${SS_RUST}.tar.gz && /apk/setup
WORKDIR ./shadowsocks-rust-${SS_RUST}/
RUN cargo fetch
RUN cargo build --release --bin sslocal --bin ssserver \
      --features "stream-cipher aead-cipher-extra aead-cipher-2022 aead-cipher-2022-extra"
WORKDIR ./target/release/
RUN mv sslocal /tmp/ss-rust-local && mv ssserver /tmp/ss-rust-server && strip /tmp/ss-rust-*
COPY --from=upx /tmp/upx /usr/bin/
RUN ls /tmp/ss-rust-* | xargs -P0 -n1 upx -9

# Compile shadowsocks-libev
FROM ${ALPINE} AS ss-libev
ENV SS_LIBEV="3.3.5"
RUN apk add c-ares-dev libev-dev libsodium-dev linux-headers mbedtls-dev pcre-dev
COPY --from=build-base /apk/ /apk/
RUN wget https://github.com/shadowsocks/shadowsocks-libev/releases/download/v${SS_LIBEV}/shadowsocks-libev-${SS_LIBEV}.tar.gz && \
    tar xf shadowsocks-libev-*.tar.gz && /apk/setup
WORKDIR ./shadowsocks-libev-${SS_LIBEV}/
RUN ./configure --disable-documentation && make
WORKDIR ./src/
RUN mv ss-local /tmp/ss-libev-local && mv ss-server /tmp/ss-libev-server && strip /tmp/ss-libev-*

# Package shadowsocks-python (lastest version, legacy version, R version aka ssr)
FROM ${PYTHON} AS ss-python
ENV SS_PYTHON="2.6.2"
RUN apk add git && mkdir -p /packages/
RUN git clone https://github.com/dnomd343/shadowsocksr.git && \
    git clone https://github.com/shadowsocks/shadowsocks.git && \
    wget https://github.com/shadowsocks/shadowsocks/archive/refs/tags/${SS_PYTHON}.tar.gz && tar xf ${SS_PYTHON}.tar.gz
# shadowsocks-python (R version)
WORKDIR /shadowsocksr/
RUN sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/ordereddict.py && \
    sed -i "/for path in paths:/a\        if 'libcrypto.so' in path:" ./shadowsocks/crypto/util.py && \
    sed -i "/libcrypto.so/a\            path = 'libcrypto.so.1.0.0'" ./shadowsocks/crypto/util.py && \
    python3 setup.py build
WORKDIR ./build/lib/shadowsocks/
RUN chmod +x local.py server.py && mv local.py server.py ../ && mv ../../lib/ /packages/ssr-python/
# shadowsocks-python (latest version)
WORKDIR /shadowsocks/
RUN git checkout master && \
    sed -i 's/if addr is/if addr ==/g' ./shadowsocks/common.py && \
    sed -i 's/and ip is not/and ip !=/g' ./shadowsocks/common.py && \
    sed -i 's/if len(block) is/if len(block) ==/g' ./shadowsocks/common.py && \
    sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    python3 setup.py build
WORKDIR ./build/lib/shadowsocks/
RUN chmod +x local.py server.py && mv local.py server.py ../ && mv ../../lib/ /packages/ss-python/
# shadowsocks-python (legacy version)
WORKDIR /shadowsocks-${SS_PYTHON}/
RUN sed -i 's/MutableMapping/abc.MutableMapping/' ./shadowsocks/lru_cache.py && \
    sed -i "s/find_library(p)/'libsodium.so.23'/g" ./shadowsocks/crypto/ctypes_libsodium.py && \
    sed -i "s/find_library(p)/'libcrypto.so.1.0.0'/g" ./shadowsocks/crypto/ctypes_openssl.py && \
    python3 setup.py build
WORKDIR ./build/lib/shadowsocks/
RUN chmod +x local.py server.py && mv local.py server.py ../ && mv ../../lib/ /packages/ss-python-legacy/

# Compile shadowsocks-bootstrap
FROM ${ALPINE} AS ss-bootstrap
RUN apk add cmake git
COPY --from=build-base /apk/ /apk/
RUN git clone https://github.com/dnomd343/shadowsocks-bootstrap.git && /apk/setup
WORKDIR ./shadowsocks-bootstrap/bin/
RUN cmake -DCMAKE_EXE_LINKER_FLAGS=-static -DCMAKE_BUILD_TYPE=Release .. && \
    make && strip ss-bootstrap-* && mv ss-bootstrap-* /tmp/

# Combine shadowsocks dependencies
FROM ${PYTHON} AS shadowsocks
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

# Pack python3 modules
FROM ${ALPINE} AS python-pkg
COPY --from=wheels /wheels/*.whl /site-packages/
COPY --from=ss-python /packages/ /site-packages/
WORKDIR /site-packages/
RUN ls *.whl | xargs -P0 -n1 unzip && rm *.whl && \
    rm -rf $(find ./ -name '__pycache__') && tar czf /packages.tar.gz ./

# Compile openssl (old version, for shadowsocks method -> idea-cfb / seed-cfb)
FROM ${ALPINE} AS openssl
ENV OPENSSL="1.0.2"
ENV OPENSSL_SUB="u"
COPY --from=build-base /apk/ /apk/
RUN apk add perl && /apk/setup
RUN wget https://www.openssl.org/source/old/${OPENSSL}/openssl-${OPENSSL}${OPENSSL_SUB}.tar.gz && tar xf openssl-*.tar.gz
WORKDIR ./openssl-${OPENSSL}${OPENSSL_SUB}/
RUN ./config --shared --prefix=/usr/ && make && mv libcrypto.so.1.0.0 /tmp/ && strip /tmp/lib*

# Compile sip003 plugins (part1 -> gcc & cargo)
FROM ${RUST} AS plugin-1
RUN apk add autoconf automake git libev-dev libtool linux-headers
COPY --from=build-base /apk/ /apk/
RUN git clone https://github.com/shadowsocks/qtun.git && \
    git clone https://github.com/shadowsocks/simple-obfs.git && \
    /apk/setup && mkdir -p /plugins/
# Compile simple-obfs
WORKDIR /simple-obfs/
RUN git submodule update --init && ./autogen.sh && ./configure --disable-documentation && \
    make && mv ./src/obfs-* /plugins/ && strip /plugins/obfs-*
# Compile qtun
WORKDIR /qtun/
RUN cargo fetch
RUN cargo build --release && cd ./target/release/ && mv qtun-client qtun-server /plugins/ && strip /plugins/qtun-*
COPY --from=upx /tmp/upx /usr/bin/
RUN ls /plugins/qtun-* | xargs -P0 -n1 upx -9

# Compile sip003 plugins (part2 -> go1.16)
FROM ${GO16} AS plugin-2
ENV GOST_PLUGIN="v1.6.3"
ENV V2RAY_PLUGIN="v1.3.2"
RUN apk add git && mkdir -p /plugins/
RUN git clone https://github.com/dnomd343/GoQuiet.git && \
    git clone https://github.com/ihciah/rabbit-tcp.git && \
    git clone https://github.com/dnomd343/rabbit-plugin.git && \
    git clone https://github.com/maskedeken/gost-plugin.git && \
    git clone https://github.com/shadowsocks/v2ray-plugin.git && \
    git clone https://github.com/IrineSistiana/mos-tls-tunnel.git
# Compile v2ray-plugin
WORKDIR /go/v2ray-plugin/
RUN git checkout ${V2RAY_PLUGIN} && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
    mv v2ray-plugin /plugins/
# Compile gost-plugin
WORKDIR /go/gost-plugin/
RUN git checkout ${GOST_PLUGIN} && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && \
    mv gost-plugin /plugins/
# Compile GoQuiet
WORKDIR /go/GoQuiet/
RUN go mod init github.com/cbeuw/GoQuiet && go mod tidy
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-client/ && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/gq-server/ && \
    mv gq-client gq-server /plugins/
# Compile mos-tls-tunnel
WORKDIR /go/mos-tls-tunnel/
RUN go mod init github.com/IrineSistiana/mos-tls-tunnel && go mod vendor
RUN env CGO_ENABLED=0 go build -v -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-client/ && \
    env CGO_ENABLED=0 go build -v -mod=vendor -trimpath -ldflags "-s -w" ./cmd/mtt-server/ && \
    mv mtt-client mtt-server /plugins/
# Compile rabbit-plugin
WORKDIR /go/rabbit-plugin/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv rabbit-plugin /plugins/
# Compile rabbit-tcp
WORKDIR /go/rabbit-tcp/cmd/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.Version=$(git describe --tags) -s -w" && mv cmd /plugins/rabbit
COPY --from=upx /tmp/upx/ /usr/bin/
RUN ls /plugins/* | xargs -P0 -n1 upx -9

# Compile sip003 plugins (part3 -> go1.18)
FROM ${GO18} AS plugin-3
ENV CLOAK="v2.6.0"
ENV SIMPLE_TLS="v0.7.0"
RUN apk add git && mkdir -p /plugins/
RUN git clone https://github.com/Qv2ray/gun.git && \
    git clone https://github.com/cbeuw/Cloak.git && \
    git clone https://github.com/dnomd343/kcptun.git && \
    git clone https://github.com/teddysun/xray-plugin.git && \
    git clone https://github.com/IrineSistiana/simple-tls.git
# Compile simple-tls
WORKDIR /go/simple-tls/
RUN git checkout ${SIMPLE_TLS} && \
    sed -i 's/version = "unknown\/dev"/version = "'$(git describe --tags)'"/g' main.go && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv simple-tls /plugins/
# Compile xray-plugin
WORKDIR /go/xray-plugin/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" && mv xray-plugin /plugins/
# Compile kcptun
WORKDIR /go/kcptun/
RUN git checkout sip003 && go mod init github.com/shadowsocks/kcptun && go mod tidy
RUN env CGO_ENABLED=0 go build -v -o kcptun-client -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./client/ && \
    env CGO_ENABLED=0 go build -v -o kcptun-server -trimpath -ldflags "-X main.VERSION=$(git describe --tags) -s -w" ./server/ && \
    mv kcptun-client kcptun-server /plugins/
# Compile Cloak
WORKDIR /go/Cloak/
RUN git checkout ${CLOAK} && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-client/ && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.version=$(git describe --tags) -s -w" ./cmd/ck-server/ && \
    mv ck-client ck-server /plugins/
# Compile gun-plugin
WORKDIR /go/gun/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" ./cmd/sip003/ && mv sip003 /plugins/gun-plugin
COPY --from=upx /tmp/upx /usr/bin/
RUN ls /plugins/* | xargs -P0 -n1 upx -9

# Combine sip003 plugins
FROM ${ALPINE} AS plugin
COPY --from=plugin-1 /plugins/ /plugins/
COPY --from=plugin-2 /plugins/ /plugins/
COPY --from=plugin-3 /plugins/ /plugins/

# Compile xray-core
FROM ${GO19} AS xray
ENV XRAY="1.6.0"
RUN wget https://github.com/XTLS/Xray-core/archive/refs/tags/v${XRAY}.tar.gz && tar xf v${XRAY}.tar.gz
WORKDIR ./Xray-core-${XRAY}/main/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv main /tmp/xray
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/xray

# Compile v2ray-core
FROM ${GO19} AS v2ray
ENV V2FLY="5.1.0"
RUN wget https://github.com/v2fly/v2ray-core/archive/refs/tags/v${V2FLY}.tar.gz && tar xf v${V2FLY}.tar.gz
WORKDIR ./v2ray-core-${V2FLY}/main/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv main /tmp/v2ray
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/v2ray

FROM ${GO19} AS sing
ENV SING="1.0.5"
RUN wget https://github.com/SagerNet/sing-box/archive/refs/tags/v${SING}.tar.gz && tar xf v${SING}.tar.gz
WORKDIR ./sing-box-${SING}/cmd/sing-box/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" \
      -tags "with_quic with_grpc with_wireguard with_shadowsocksr with_ech with_utls" && mv sing-box /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/sing-box

# Compile trojan-go
FROM ${GO18} AS trojan-go
ENV TROJAN_GO="v0.10.6"
RUN apk add git && git clone https://github.com/p4gefau1t/trojan-go.git
WORKDIR ./trojan-go/
RUN git checkout ${TROJAN_GO} && go get -d
RUN env CGO_ENABLED=0 go build -v -tags "full" -trimpath -ldflags " \
      -X github.com/p4gefau1t/trojan-go/constant.Version=$(git describe --dirty) \
      -X github.com/p4gefau1t/trojan-go/constant.Commit=$(git rev-parse HEAD) -s -w" && \
    mv trojan-go /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/trojan-go

# Compile trojan
FROM ${ALPINE} AS trojan
ENV TROJAN="1.16.0"
RUN apk add boost-dev cmake openssl-dev
COPY --from=build-base /apk/ /apk/
RUN wget https://github.com/trojan-gfw/trojan/archive/refs/tags/v${TROJAN}.tar.gz && \
    tar xf v${TROJAN}.tar.gz && /apk/setup
WORKDIR ./trojan-${TROJAN}/build/
RUN cmake -DENABLE_MYSQL=OFF -DSYSTEMD_SERVICE=OFF .. && make && strip trojan && mv trojan /tmp/
COPY --from=trojan-go /tmp/trojan-go /tmp/

# Compile gost and gost-v3
FROM ${GO19} AS gost
ENV GOST="2.11.4"
ENV GOST_V3="3.0.0-beta.5"
RUN wget https://github.com/ginuerzh/gost/archive/refs/tags/v${GOST}.tar.gz && tar xf v${GOST}.tar.gz && \
    wget https://github.com/go-gost/gost/archive/refs/tags/v${GOST_V3}.tar.gz && tar xf v${GOST_V3}.tar.gz
WORKDIR /go/gost-${GOST}/cmd/gost/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv gost /tmp/
WORKDIR /go/gost-${GOST_V3}/cmd/gost/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv gost /tmp/gost-v3
COPY --from=upx /tmp/upx /usr/bin/
RUN ls /tmp/gost* | xargs -P0 -n1 upx -9

# Compile brook
FROM ${GO16} AS brook
ENV BROOK="20221010"
RUN wget https://github.com/txthinking/brook/archive/refs/tags/v${BROOK}.tar.gz && tar xf v${BROOK}.tar.gz
WORKDIR ./brook-${BROOK}/cli/brook/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w" && mv brook /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/brook

# Compile clash
FROM ${GO19} AS clash
ENV CLASH="1.11.8"
RUN wget https://github.com/Dreamacro/clash/archive/refs/tags/v${CLASH}.tar.gz && tar xf v${CLASH}.tar.gz
WORKDIR ./clash-${CLASH}/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w \
      -X 'github.com/Dreamacro/clash/constant.Version=${CLASH}' \
      -X 'github.com/Dreamacro/clash/constant.BuildTime=$(date -u)'" && \
    mv clash /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/clash

# Download naiveproxy
FROM ${ALPINE} AS naive
ENV NAIVE="v106.0.5249.91-1"
COPY --from=build-base /apk/ /apk/
RUN apk add curl libgcc jq && /apk/setup
RUN curl -sL https://api.github.com/repos/klzgrad/naiveproxy/releases/tags/${NAIVE} \
      | jq .assets | jq .[].name | grep naiveproxy-${NAIVE}-openwrt-$(uname -m) \
      | cut -b 2- | rev | cut -b 2- | rev | tac > list.dat
RUN echo "while read FILE_NAME; do" >> naive.sh && \
    echo "wget https://github.com/klzgrad/naiveproxy/releases/download/\${NAIVE}/\${FILE_NAME}" >> naive.sh && \
    echo "tar xf \${FILE_NAME} && ldd ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive" >> naive.sh && \
    echo "[ \$? -eq 0 ] && cp ./\$(echo \$FILE_NAME | rev | cut -b 8- | rev)/naive /tmp/ && break" >> naive.sh && \
    echo "done < list.dat" >> naive.sh && sh naive.sh && strip /tmp/naive

# Compile open-snell
FROM ${GO18} AS snell
ENV SNELL="3.0.1"
RUN wget https://github.com/icpz/open-snell/archive/refs/tags/v${SNELL}.tar.gz && tar xf v${SNELL}.tar.gz
WORKDIR ./open-snell-${SNELL}/
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags \
      "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL}'" ./cmd/snell-client/ && \
    env CGO_ENABLED=0 go build -v -trimpath -ldflags \
      "-s -w -X 'github.com/icpz/open-snell/constants.Version=${SNELL}'" ./cmd/snell-server/ && \
    mv snell-client snell-server /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN ls /tmp/snell-* | xargs -P0 -n1 upx -9

# Compile hysteria
FROM ${GO19} AS hysteria
ENV HYSTERIA="v1.2.1"
RUN apk add git
RUN git clone https://github.com/HyNetwork/hysteria.git
WORKDIR ./hysteria/cmd/
RUN git checkout ${HYSTERIA} && go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-s -w \
      -X 'main.appVersion=$(git describe --tags)' \
      -X 'main.appCommit=$(git rev-parse HEAD)' \
      -X 'main.appDate=$(date "+%F %T")'" && \
    mv cmd /tmp/hysteria
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/hysteria

# Compile relaybaton
FROM ${GO14} AS relaybaton
ENV RELAYBATON="0.6.0"
RUN apk add build-base git perl rsync
RUN wget https://github.com/iyouport-org/relaybaton/archive/refs/tags/v${RELAYBATON}.tar.gz && tar xf v${RELAYBATON}.tar.gz
WORKDIR ./relaybaton-${RELAYBATON}/cmd/cli/
RUN go get -d
WORKDIR ../../
RUN make && mv ./bin/relaybaton /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/relaybaton

# Compile dnsproxy
FROM ${GO18} AS dnsproxy
ENV DNSPROXY="0.45.2"
RUN wget https://github.com/AdguardTeam/dnsproxy/archive/refs/tags/v${DNSPROXY}.tar.gz && tar xf v${DNSPROXY}.tar.gz
WORKDIR ./dnsproxy-${DNSPROXY}/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -trimpath -ldflags "-X main.VersionString=${DNSPROXY} -s -w" && mv dnsproxy /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/dnsproxy

# Compile mad
FROM ${GO16} AS mad
ENV MAD="20210401"
RUN wget https://github.com/txthinking/mad/archive/refs/tags/v${MAD}.tar.gz && tar xf v${MAD}.tar.gz
WORKDIR ./mad-${MAD}/cli/mad/
RUN go get -d
RUN env CGO_ENABLED=0 go build -v -ldflags="-s -w" && mv mad /tmp/
COPY --from=upx /tmp/upx /usr/bin/
RUN upx -9 /tmp/mad

# Combine all release
FROM ${PYTHON} AS build
COPY --from=python-pkg /packages.tar.gz /
ARG PYTHON="3.10"
WORKDIR /release/usr/local/lib/python${PYTHON}/site-packages/
RUN tar xf /packages.tar.gz -C ./
COPY --from=openssl /tmp/libcrypto.so* /release/lib/
COPY --from=shadowsocks /release/ /release/usr/bin/
COPY --from=plugin /plugins/ /release/usr/bin/
COPY --from=xray /tmp/xray /release/usr/bin/
COPY --from=v2ray /tmp/v2ray /release/usr/bin/
COPY --from=sing /tmp/sing-box /release/usr/bin/
COPY --from=trojan /tmp/trojan* /release/usr/bin/
COPY --from=gost /tmp/gost* /release/usr/bin/
COPY --from=brook /tmp/brook /release/usr/bin/
COPY --from=clash /tmp/clash /release/usr/bin/
COPY --from=naive /tmp/naive /release/usr/bin/
COPY --from=snell /tmp/snell-* /release/usr/bin/
COPY --from=hysteria /tmp/hysteria /release/usr/bin/
COPY --from=relaybaton /tmp/relaybaton /release/usr/bin/
COPY --from=dnsproxy /tmp/dnsproxy /release/usr/bin/
COPY --from=mad /tmp/mad /release/usr/bin/
COPY ./ /release/usr/local/share/ProxyC/

# Release proxyc image
FROM ${PYTHON}
RUN apk add --no-cache boost-program_options c-ares ca-certificates libev libsodium libstdc++ mbedtls pcre && \
    ln -s /usr/local/share/ProxyC/Main.py /usr/bin/proxyc
COPY --from=build /release/ /
EXPOSE 7839
ENTRYPOINT ["proxyc"]
