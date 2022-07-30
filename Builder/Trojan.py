#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Builder import Xray


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    outboundConfig = {
        'protocol': 'trojan',
        'settings': {
            'servers': [{**{
                'address': proxyInfo['server'],
                'port': proxyInfo['port'],
                'password': proxyInfo['passwd'],
            }, **Xray.xtlsFlow(proxyInfo['stream'])}]
        },
        'streamSettings': Xray.loadStream(proxyInfo['stream'])
    }
    trojanConfig = Xray.loadConfig(socksInfo, outboundConfig)  # load config file for xray-core
    return ['xray', '-c', configFile], json.dumps(trojanConfig), {}
