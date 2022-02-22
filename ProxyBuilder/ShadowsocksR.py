#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

ssrMethodList = [ # ShadowsocksR加密方式
    'aes-128-cfb',
    'aes-192-cfb',
    'aes-256-cfb',
    'aes-128-cfb1',
    'aes-192-cfb1',
    'aes-256-cfb1',
    'aes-128-cfb8',
    'aes-192-cfb8',
    'aes-256-cfb8',
    'aes-128-ctr',
    'aes-192-ctr',
    'aes-256-ctr',
    'aes-128-gcm',
    'aes-192-gcm',
    'aes-256-gcm',
    'aes-128-ofb',
    'aes-192-ofb',
    'aes-256-ofb',
    'camellia-128-cfb',
    'camellia-192-cfb',
    'camellia-256-cfb',
    'none',
    'table',
    'rc4',
    'rc4-md5',
    'rc4-md5-6',
    'bf-cfb',
    'cast5-cfb',
    'des-cfb',
    'idea-cfb',
    'seed-cfb',
    'rc2-cfb',
    'salsa20',
    'xsalsa20',
    'chacha20',
    'xchacha20',
    'chacha20-ietf',
]

ssrProtocolList = [ # ShadowsocksR协议列表
    'origin',
    'verify_sha1',
    'verify_simple',
    'verify_deflate',
    'auth_simple',
    'auth_sha1',
    'auth_sha1_v2',
    'auth_sha1_v4',
    'auth_aes128',
    'auth_aes128_md5',
    'auth_aes128_sha1',
    'auth_chain_a',
    'auth_chain_b',
    'auth_chain_c',
    'auth_chain_d',
    'auth_chain_e',
    'auth_chain_f',
]

ssrObfsList = [ # ShadowsocksR混淆方式
    'plain',
    'http_post',
    'http_simple',
    'tls_simple',
    'tls1.2_ticket_auth',
    'tls1.2_ticket_fastauth',
    'random_head',
]

def __ssrFormatCheck(proxyInfo: dict) -> bool:  # ShadowsocksR参数检查
    if 'server' not in proxyInfo or not isinstance(proxyInfo['server'], str): # server -> str
        return False
    if 'port' not in proxyInfo or not isinstance(proxyInfo['port'], int): # port -> int
        return False
    if 'method' not in proxyInfo or not isinstance(proxyInfo['method'], str): # method -> str
        return False
    if 'passwd' not in proxyInfo or not isinstance(proxyInfo['passwd'], str): # passwd -> str
        return False
    if 'protocol' not in proxyInfo or not isinstance(proxyInfo['protocol'], str): # protocol -> str
        return False
    if 'protocolParam' not in proxyInfo or not isinstance(proxyInfo['protocolParam'], str): # protocolParam -> str
        return False
    if 'obfs' not in proxyInfo or not isinstance(proxyInfo['obfs'], str): # obfs -> str
        return False
    if 'obfsParam' not in proxyInfo or not isinstance(proxyInfo['obfsParam'], str): # obfsParam -> str
        return False
    return True

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
    if not __ssrFormatCheck(proxyInfo): # 参数有误
        return None, None, None
    if not proxyInfo['method'] in ssrMethodList: # 匹配不到加密方法
        return None, None, None
    if not proxyInfo['protocol'] in ssrProtocolList: # 匹配不到协议
        return None, None, None
    if not proxyInfo['obfs'] in ssrObfsList: # 匹配不到混淆方式
        return None, None, None
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
