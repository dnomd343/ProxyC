#!/usr/bin/python
# -*- coding:utf-8 -*-

import ProxyFilter as Filter

info = {
    'type': 'vless',
    'server': '127.0.0.1',
    'port': '12345',
    'id': 'dnomd343',
    'stream': {
        'type': 'grpc',
        'service': 'dnomd343',
        'secure': {
            'type': 'tls',
            'sni': '',
            'flow': 'xtls-origin',
            'udp443': True
        }
    }
}

ret = Filter.filte(info)

print(ret[0])
print(ret[1])
