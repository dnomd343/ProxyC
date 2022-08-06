#!/usr/bin/env python

from pprint import pprint
from Basis.Filter import Filter
from Basis.Filter import filterObject
from Filter.Shadowsocks import ssObject
from Filter.ShadowsocksR import ssrObject

# pprint(ssObject, sort_dicts = False)
# pprint(ssrObject, sort_dicts = False)
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

# ret = Filter(ssProxy, ssObject)
ret = Filter(ssrProxy, ssrObject)
pprint(ret, sort_dicts = False)
