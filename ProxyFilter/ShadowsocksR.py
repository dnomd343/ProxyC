#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

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

ssrProtocolList = [ # ShadowsocksR协议
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

def __ssrProtocol(protocol) -> str:
    protocol = baseFunc.toStrTidy(protocol).replace('-', '_')
    if protocol == '':
        return 'origin'
    return protocol

def __ssrObfs(obfs) -> str:
    obfs = baseFunc.toStrTidy(obfs).replace('-', '_')
    if obfs == '':
        return 'plain'
    return obfs

ssrFilterRules = {
    'rootObject': {
        'remark': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'group': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'server': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': baseFunc.isHost,
            'errMsg': 'Illegal server address'
        },
        'port': {
            'optional': True,
            'type': int,
            'format': baseFunc.toInt,
            'filter': baseFunc.isPort,
            'errMsg': 'Illegal port number'
        },
        'method': {
            'optional': True,
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
            'filter': lambda method: method in ssrMethodList,
            'errMsg': 'Unknown ShadowsocksR method'
        },
        'passwd': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'protocol': {
            'optional': False,
            'default': 'origin',
            'type': str,
            'format': __ssrProtocol,
            'filter': lambda protocol: protocol in ssrProtocolList,
            'errMsg': 'Unknown ShadowsocksR protocol'
        },
        'protocolParam': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'obfs': {
            'optional': False,
            'default': 'plain',
            'type': str,
            'format': __ssrObfs,
            'filter': lambda obfs: obfs in ssrObfsList,
            'errMsg': 'Unknown ShadowsocksR obfs'
        },
        'obfsParam': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        }
    }
}

def ssrFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    ShadowsocksR节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'ssr',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            ssrFilterRules['rootObject'].pop('remark')
            ssrFilterRules['rootObject'].pop('group')
        status, result = baseFunc.ruleFilter(rawInfo, ssrFilterRules, {
            'type': 'ssr'
        })
        if not status: # 节点格式错误
            return False, result
        if result['protocol'] == 'origin': # origin无参数
            result['protocolParam'] = ''
        if result['obfs'] == 'plain': # plain无参数
            result['obfsParam'] = ''
        return True, result
    except:
        return False, 'Unknown error'
