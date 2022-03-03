#!/usr/bin/python
# -*- coding:utf-8 -*-

def __originConfig(proxyInfo: dict) -> list:
    return [
        'client',
        '--server', proxyInfo['server'] + ':' + str(proxyInfo['port']),
        '--password', proxyInfo['passwd']
    ]

def __wsConfig(proxyInfo: dict) -> list:
    return [
        'wsclient',
        '--wsserver', 'ws://' + proxyInfo['ws']['host'] + ':' + str(proxyInfo['port']) + proxyInfo['ws']['path'],
        '--address', proxyInfo['server'] + ':' + str(proxyInfo['port']),
        '--password', proxyInfo['passwd']
    ]

def __wssConfig(proxyInfo: dict) -> list:
    wssConfig = [
        'wssclient',
        '--wssserver', 'wss://' + proxyInfo['ws']['host'] + ':' + str(proxyInfo['port']) + proxyInfo['ws']['path'],
        '--address', proxyInfo['server'] + ':' + str(proxyInfo['port']),
        '--password', proxyInfo['passwd']
    ]
    if not proxyInfo['ws']['secure']['verify']:
        wssConfig += ['--insecure']
    return wssConfig

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list, str or None, dict]:
    """
    Brook配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    command = [
        'brook',
        '--debug', '--listen', 'skip success', # debug on
    ]
    if proxyInfo['ws'] is None:
        command += __originConfig(proxyInfo) # original mode
    elif proxyInfo['ws']['secure'] is None:
        command += __wsConfig(proxyInfo) # ws mode
    else:
        command += __wssConfig(proxyInfo) # wss mode
    command += [
        '--socks5', '127.0.0.1:' + str(socksPort)
    ]
    return command, None, {}
