#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list or None, str or None, dict or None]:
    """
    ShadowsocksR配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

        节点有误:
            return None, None, None

        载入成功:
            return startCommand, fileContent, envVar
    """
    try:
        config = {
            'server': proxyInfo['server'],
            'server_port': proxyInfo['port'],
            'local_address': '127.0.0.1',
            'local_port': socksPort,
            'password': proxyInfo['passwd'],
            'method': proxyInfo['method'],
            'protocol': proxyInfo['protocol'],
            'protocol_param': proxyInfo['protocolParam'],
            'obfs': proxyInfo['obfs'],
            'obfs_param': proxyInfo['obfsParam']
        }
        return ['ssr-local', '-c', configFile], json.dumps(config), {}
    except:
        return None, None, None
