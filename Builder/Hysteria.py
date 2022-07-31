#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Basis.Functions import hostFormat


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    hysteriaConfig = {**{
        'server': '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port']),
        'protocol': proxyInfo['protocol'],
        'up_mbps': proxyInfo['up'],
        'down_mbps': proxyInfo['down'],
        'socks5': {
            'listen': '%s:%i' % (hostFormat(socksInfo['addr'], v6Bracket = True), socksInfo['port'])
        }
    }, **({} if proxyInfo['obfs'] is None else {
        'obfs': proxyInfo['obfs']
    }), **({} if proxyInfo['passwd'] is None else {
        'auth_str': proxyInfo['passwd']
    }), **({} if proxyInfo['sni'] == '' else {
        'server_name': proxyInfo['sni']
    }), **({} if proxyInfo['alpn'] is None else {
        'alpn': proxyInfo['alpn']
    }), **({} if proxyInfo['verify'] else {
        'insecure': True
    })}
    return ['hysteria', '-c', configFile, 'client'], json.dumps(hysteriaConfig), {}
