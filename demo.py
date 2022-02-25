#!/usr/bin/python
# -*- coding:utf-8 -*-
import copy
import time

import ProxyFilter as Filter
import ProxyBuilder as Builder

# info = {
#     'type': 'vless',
#     'server': '127.0.0.1',
#     'port': '12345',
#     'id': 'dnomd343',
#     'stream': {
#         'type': 'grpc',
#         'service': 'dnomd343',
#         'secure': {
#             'type': 'tls',
#             'sni': '',
#             'flow': 'xtls-origin',
#             'udp443': True
#         }
#     }
# }
#
# ret = Filter.filte(info)
#
# print(ret[0])
# print(ret[1])

info = {
    'type': 'vless',
    'server': '127.0.0.1',
    'port': '12345',
    'id': '58c0f2eb-5d47-45d0-8f5f-ebae5c2cfdd9',
    'stream': {
        'type': 'tcp',
        'secure': {
            'type': 'xtls',
            'udp443': True
        }
    }
}

info = copy.deepcopy(Filter.filte(info)[1])
print(info)
Builder.build(info, '/tmp/ProxyC')
time.sleep(5)
Builder.destroy(info)
