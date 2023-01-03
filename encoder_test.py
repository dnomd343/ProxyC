#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Encoder
from Filter import Filter

vless_demo_1 = {
    'type': 'vless',
    'name': '🇭🇰 DataGrids DMIT XTLS 1Gbps',
    'info': {
        'server': '54.142.232.16',
        'port': 52227,
        'method': 'none',
        'id': '75e6edee-2c30-41b0-9d88-676c4fb19ee8',
        'stream': {
            'type': 'tcp',
            'obfs': None,
            'secure': {
                'type': 'xtls',
                'sni': 'proxy.demo.com',
                'alpn': None,
                'verify': True,
                'flow': 'xtls-direct',
                'udp443': False
            }
        }
    }
}

vmess_demo_1 =   {
    'type': 'vmess',
    'name': '🇭🇰 DataGrids DMIT VMess 1Gbps',
    'info': {
        'server': '54.142.232.16',
        'port': 52227,
        'method': 'auto',
        'id': '75e6edee-2c30-41b0-9d88-676c4fb19ee8',
        'aid': 0,
        'stream': {
            'type': 'ws',
            'host': 'proxy.demo.com',
            'path': '/vmessws',
            'ed': 2048,
            'secure': {
                'sni': 'proxy.demo.com',
                'alpn': None,
                'verify': True
            }
        }
    }
}

vless_demo_1['info'] = Filter('vless', vless_demo_1['info'])
vmess_demo_1['info'] = Filter('vmess', vmess_demo_1['info'])
# print(vless_demo_1)
# print(vmess_demo_1)

print(Encoder.v2rayN(vmess_demo_1['info'], 'demo'))
