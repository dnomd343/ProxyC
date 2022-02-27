#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
from ProxyBuilder import Xray

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list, str, dict]:
    """
    Trojan配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    flowType = None
    if proxyInfo['stream']['secure'] is not None and proxyInfo['stream']['secure']['type'] == 'xtls':
        flowType = proxyInfo['stream']['secure']['flow']
        if flowType == 'xtls-origin':
            flowType = 'xtls-rprx-origin'
        elif flowType == 'xtls-direct':
            flowType = 'xtls-rprx-direct'
        elif flowType == 'xtls-splice':
            flowType = 'xtls-rprx-splice'
        else:
            raise Exception('Unknown XTLS flow')
        if proxyInfo['stream']['secure']['udp443']:
            flowType += '-udp443'
    outboundConfig = {
        'protocol': 'trojan',
        'settings': {
            'servers': [
                {
                    'address': proxyInfo['server'],
                    'port': proxyInfo['port'],
                    'password': proxyInfo['passwd'],
                }
            ]
        },
        'streamSettings': Xray.xrayStreamConfig(proxyInfo['stream'])
    }
    if flowType is not None: # 添加XTLS流控类型
        outboundConfig['settings']['servers'][0]['flow'] = flowType
    config = Xray.baseConfig(socksPort, outboundConfig) # Trojan节点配置
    return ['xray', '-c', configFile], json.dumps(config), {}
