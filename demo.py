#!/usr/bin/python
# -*- coding:utf-8 -*-
import copy
import time

import Check as Checker
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
#
# info = {
#     'type': 'vless',
#     'server': '127.0.0.1',
#     'port': '12345',
#     'id': '58c0f2eb-5d47-45d0-8f5f-ebae5c2cfdd9',
#     'stream': {
#         'type': 'tcp',
#         'secure': {
#             'type': 'xtls',
#             'udp443': True
#         }
#     }
# }
#
# info = copy.deepcopy(Filter.filte(info)[1])
# print(info)
# Builder.build(info, '/tmp/ProxyC')
# time.sleep(5)
# Builder.destroy(info)

# info = {
#     'type': 'vmess',
#     'server': '127.0.0.1',
#     'port': 12345,
#     'id': '1f7aa040-94d8-4b53-ae85-af6946d550bb',
#     'stream': {
#         'type': 'h2',
#         # 'host': 'dns.343.re',
#         # 'path': '/test',
#         # 'secure': {}
#         # 'secure': {
#         #     'sni': 'dns.343.re'
#         # }
#     }
# }
#
# ret = Filter.filte(info)
#
# print(ret[0])
# print(ret[1])

info = {
    'type': 'vmess',
    'server': '127.0.0.1',
    'port': '3345',
    'id': '657b26d0-d25e-5b75-a018-40cb679c83a3',
    'stream': {
        'type': 'ws',
        'host': None,
        'path': '/test',
        'ed': 2048,
        'secure': {
            'sni': 'dns.343.re',
            'alpn': 'h2,http/1.1'
        }
    }
}

ret = Filter.filte(info)

print(ret[0])
print(ret[1])

data = Checker.proxyTest({
    'check': ['http'],
    'info': ret[1]
})

print(data)
