#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
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
    config['net'] = stream['type']

    if stream['type'] == 'tcp':
        if stream['obfs'] is None:
            config.update({
                'type': 'none',
                'host': '',
                'path': '',
            })
        else:
            config.update({
                'type': 'http',
                'host': stream['obfs']['host'],
                'path': stream['obfs']['path'],
            })
    elif stream['type'] == 'kcp':
        config.update({
            'type': stream['obfs'],
            'host': '',
            'path': '' if stream['seed'] is None else stream['seed'],
        })
    elif stream['type'] == 'ws':
        config.update({
            'type': 'none',
            'host': stream['host'],
            'path': stream['path'],  # TODO: add `ed` field
        })
    elif stream['type'] == 'h2':
        config.update({
            'type': 'none',
            'host': stream['host'],
            'path': stream['path'],
        })
    elif stream['type'] == 'quic':
        config.update({
            'type': stream['obfs'],
            'host': stream['method'],
            'path': stream['passwd'],
        })
    elif stream['type'] == 'grpc':
        config.update({
            'type': stream['mode'],
            'host': '',
            'path': stream['service'],
        })

    secure = stream['secure']
    if secure is None:  # without TLS secure layer
        config.update({
            'tls': '',
            'sni': '',
            'alpn': '',
        })
    else:
        config.update({
            'tls': 'tls',
            'sni': secure['sni'],
            'alpn': '' if secure['alpn'] is None else secure['alpn'],
        })

    return 'vmess://%s' % b64Encode(
        json.dumps(config, indent = 2).replace('\n', '\r\n'),
        urlSafe = False,
        padding = True,
    )
