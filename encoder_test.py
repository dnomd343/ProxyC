#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

vless_demo_1['info'] = Filter('vless', vless_demo_1['info'])

print(vless_demo_1)
