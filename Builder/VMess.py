#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Builder import V2ray
from Utils.Constant import vmessMethods
from Utils.Exception import buildException


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    if proxyInfo['method'] not in vmessMethods:
        raise buildException('Unknown VMess method')
    outboundConfig = {
        'protocol': 'vmess',
        'settings': {
            'vnext': [{
                'address': proxyInfo['server'],
                'port': proxyInfo['port'],
                'users': [{
                    'id': proxyInfo['id'],
                    'alterId': proxyInfo['aid'],
                    'security': proxyInfo['method']
                }]
            }]
        },
        'streamSettings': V2ray.loadStream(proxyInfo['stream'])
    }
    vmessConfig = V2ray.loadConfig(socksInfo, outboundConfig)  # load config file for v2ray-core
    return ['v2ray', 'run', '-c', configFile], json.dumps(vmessConfig), {}  # command, fileContent, envVar
