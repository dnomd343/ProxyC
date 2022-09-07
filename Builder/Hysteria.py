#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Utils.Common import v6AddBracket


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    hysteriaConfig = {
        'server': '%s:%i' % (v6AddBracket(proxyInfo['server']), proxyInfo['port']),
        'protocol': proxyInfo['protocol'],
        'up_mbps': proxyInfo['up'],
        'down_mbps': proxyInfo['down'],
        'retry_interval': 2,
        'retry': 3,
        'socks5': {
            'listen': '%s:%i' % (v6AddBracket(socksInfo['addr']), socksInfo['port'])
        },
        **({} if proxyInfo['obfs'] is None else {
            'obfs': proxyInfo['obfs']
        }),
        **({} if proxyInfo['passwd'] is None else {
            'auth_str': proxyInfo['passwd']
        }),
        **({} if proxyInfo['sni'] == '' else {
            'server_name': proxyInfo['sni']
        }),
        **({} if proxyInfo['alpn'] is None else {
            'alpn': proxyInfo['alpn']
        }),
        **({} if proxyInfo['verify'] else {
            'insecure': True
        })
    }
    return ['hysteria', '-c', configFile, 'client'], \
        json.dumps(hysteriaConfig), {'LOGGING_LEVEL': 'trace'}  # command, fileContent, envVar
