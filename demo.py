#!/usr/bin/env python

from pprint import pprint
from Basis.Filter import Filter
from Basis.Filter import filterObject
from Filter.Shadowsocks import ssObject

# pprint(ssObject, sort_dicts = False)
# pprint(filterObject, sort_dicts = False)

ssProxy = {
    'server': '1.1.1.1',
    'port': '12345',
    'method': 'none',
    'passwd': 'dnomd343',
    'plugin': {
        'type': 'obfs',

    }
}
ret = Filter(ssProxy, ssObject)
pprint(ret, sort_dicts = False)
