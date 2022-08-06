#!/usr/bin/env python

from pprint import pprint
from Basis.Filter import Filter
from Basis.Filter import filterObject
from Filter.Shadowsocks import ssObject
from Filter.ShadowsocksR import ssrObject
from Filter.VMess import vmessObject
from Filter.VLESS import vlessObject
from Filter.Trojan import trojanObject
from Filter.TrojanGo import trojanGoObject
from Filter.Brook import brookObject
from Filter.Hysteria import hysteriaObject

# pprint(ssObject, sort_dicts = False)
# pprint(ssrObject, sort_dicts = False)
# pprint(vmessObject, sort_dicts = False)
# pprint(vlessObject, sort_dicts = False)
# pprint(trojanObject, sort_dicts = False)
# pprint(trojanGoObject, sort_dicts = False)
# pprint(brookObject, sort_dicts = False)
# pprint(hysteriaObject, sort_dicts = False)
# pprint(filterObject, sort_dicts = False)

ssProxy = {
    'server': '1.1.1.1',
    'port': '12345',
    'method': 'none',
    'passwd': 'dnomd343',
    'plugin': {
        'type': 'obfs'
    }
}

ssrProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'method': 'table',
    'passwd': 'dnomd343',
    'protocol': 'auth_chain-a',
    'obfs': 'http_post'
}

vmessProxy = {
    'server': '1.1.1.1',
    'port': b'12345',
    'id': 'c8783403-64d5-4b6d-8cf4-bd3988d01b6c',
    'aid': '64',
    'stream': {
        'type': 'GRPC',
        'service': 'no-gfw',
        'mode': '  multi  ',
        'secure': {
            'sni': '  DNOMD343.top',
            'alpn': 'h2,   http/1.1',
            'verify': 'False  '
        }
    }
}

vlessProxy = {
    'server': '1.1.1.1',
    'port': r'12345',
    'method': 'NONE',
    'id': '  3f163adf-5bdd-40d0-b0ec-e47f9bebcac7',
    'stream': {
        'type': 'grpc',
        'service': 'dnomd343',
        'secure': None,
        # 'secure': {
        #     'type': 'tls',
        #     'sni': '23333',
        #     'alpn': 'h2',
        #     'verify': 0
        # }
        # 'secure': {
        #     'type': 'xtls',
        #     'sni': '23333',
        #     'alpn': 'h2',
        #     'verify': True,
        #     'flow': 'xtls-rprx-direct',
        #     'udp443': 0.1
        # }
    }
}

trojanProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'passwd': b'dnomd343',
    'stream': {
        'type': 'grpc',
        'service': 'dnomd343',
        # 'secure': None,
        'secure': {
            'type': 'tls',
            'sni': '23333',
            'alpn': 'h2',
            'verify': 0
        }
        # 'secure': {
        #     'type': 'xtls',
        #     'sni': '23333',
        #     'alpn': 'h2',
        #     'verify': True,
        #     'flow': 'xtls-rprx-direct',
        #     'udp443': 0.1
        # }
    }
}

trojanGoProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'sni': '343.re',
    'alpn': ' h2',
    'verify': 'FALSE',
    'ws': {
        'host': 'dnomd343.top',
        'path': '/test',
    },
    'ss': {
        'method': 'chacha20-ietf-poly1305',
        'passwd': 'dnomd343',
    },
    'plugin': {
        'type': 'go-quiet',
        'param': 123
    }
}

brookProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'stream': {
        'type': 'ws',
        'host': '343.re',
        'path': '/test',
        'raw': True,
        'secure': {
            'verify': '  0'
        }
    },
}

hysteriaProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'protocol': 'faketcp',
    'obfs': '1234',
    'passwd': 'dnomd343',
    'up': 100,
    'down': 500,
    'sni': '343.re',
    'alpn': 'h3',
    'verify': 'FALSE',
}

# ret = Filter(ssProxy, ssObject)
# ret = Filter(ssrProxy, ssrObject)
# ret = Filter(vmessProxy, vmessObject)
# ret = Filter(vlessProxy, vlessObject)
# ret = Filter(trojanProxy, trojanObject)
# ret = Filter(trojanGoProxy, trojanGoObject)
# ret = Filter(brookProxy, brookObject)
ret = Filter(hysteriaProxy, hysteriaObject)
pprint(ret, sort_dicts = False)
