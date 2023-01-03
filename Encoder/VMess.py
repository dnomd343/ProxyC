#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils.Common import b64Encode
from Utils.Common import urlEncode


def v2rayN(info: dict, name: str) -> str:
    """
    https://github.com/2dust/v2rayN/wiki/%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E6%A0%BC%E5%BC%8F%E8%AF%B4%E6%98%8E(ver-2)

    FORMAT: vmess://BASE64-ENCODED-JSON-STRING
            fields => v(=2) / ps / add / port / id / aid / scy / net / type / host / path / tls / sni / alpn
    """
    # TODO: base64 with `+` and `/`
    # TODO:   => not urlSafe and with padding
    config = {
        'v': '2',
        'ps': urlEncode(name),
        'add': info['server'],
        'port': str(info['port']),
        'id': info['id'],
        'aid': str(info['aid']),
        'scy': info['method'],
    }

    stream = info['stream']
    if stream['type'] == 'tcp':

        ...
    elif stream['type'] == 'kcp':
        ...
    elif stream['type'] == 'ws':
        ...
    elif stream['type'] == 'h2':
        ...
    elif stream['type'] == 'quic':
        ...
    elif stream['type'] == 'grpc':
        ...

    print(config)
    print(info)
