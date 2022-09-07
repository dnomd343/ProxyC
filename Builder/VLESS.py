#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Builder import Xray
from Utils.Exception import buildException


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    if proxyInfo['method'] != 'none':
        raise buildException('Unknown VLESS method')
    outboundConfig = {
        'protocol': 'vless',
        'settings': {
            'vnext': [{
                'address': proxyInfo['server'],
                'port': proxyInfo['port'],
                'users': [{
                    'id': proxyInfo['id'],
                    'encryption': proxyInfo['method'],
                    **Xray.xtlsFlow(proxyInfo['stream'])  # add xtls flow option
                }]
            }]
        },
        'streamSettings': Xray.loadStream(proxyInfo['stream'])
    }
    vlessConfig = Xray.loadConfig(socksInfo, outboundConfig)  # load config file for xray-core
    return ['xray', '-c', configFile], json.dumps(vlessConfig), {}  # command, fileContent, envVar
