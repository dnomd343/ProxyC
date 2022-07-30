#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Builder import Xray


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    outboundConfig = {
        'protocol': 'vless',
        'settings': {
            'vnext': [{
                'address': proxyInfo['server'],
                'port': proxyInfo['port'],
                'users': [{**{
                    'id': proxyInfo['id'],
                    'encryption': proxyInfo['method']
                }, **Xray.xtlsFlow(proxyInfo['stream'])}]
            }]
        },
        'streamSettings': Xray.loadStream(proxyInfo['stream'])
    }
    vlessConfig = Xray.loadConfig(socksInfo, outboundConfig)  # load config file for xray-core
    return ['xray', '-c', configFile], json.dumps(vlessConfig), {}
