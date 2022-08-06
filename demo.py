#!/usr/bin/env python

from pprint import pprint
from Basis.Filter import Filter
from Basis.Filter import filterObject
from Filter.Shadowsocks import ssObject
from Filter.ShadowsocksR import ssrObject
from Filter.VMess import vmessObject

# pprint(ssObject, sort_dicts = False)
# pprint(ssrObject, sort_dicts = False)
# pprint(vmessObject, sort_dicts = False)
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

# ret = Filter(ssProxy, ssObject)
# ret = Filter(ssrProxy, ssrObject)
ret = Filter(vmessProxy, vmessObject)
pprint(ret, sort_dicts = False)
