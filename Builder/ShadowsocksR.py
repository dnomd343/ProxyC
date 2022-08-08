#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Basis.Exception import buildException
from Basis.Constant import ssrMethods, ssrProtocols, ssrObfuscations


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    if proxyInfo['method'] not in ssrMethods:
        raise buildException('Unknown shadowsocksr method')
    if proxyInfo['protocol'] not in ssrProtocols:
        raise buildException('Unknown shadowsocksr protocol')
    if proxyInfo['obfs'] not in ssrObfuscations:
        raise buildException('Unknown shadowsocksr obfuscation')
    ssrConfig = {
        'server': proxyInfo['server'],
        'server_port': proxyInfo['port'],  # type -> int
        'local_address': socksInfo['addr'],
        'local_port': socksInfo['port'],  # type -> int
        'password': proxyInfo['passwd'],
        'method': proxyInfo['method'],
        'protocol': proxyInfo['protocol'],
        'protocol_param': proxyInfo['protocolParam'],
        'obfs': proxyInfo['obfs'],
        'obfs_param': proxyInfo['obfsParam']
    }
    return ['ssr-local', '-vv', '-c', configFile], json.dumps(ssrConfig), {}  # command, fileContent, envVar
