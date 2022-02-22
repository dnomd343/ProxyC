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

def __ssrFill(raw: dict) -> dict: # 补全可选值
    try:
        if 'protocol' not in raw:
            raw['protocol'] = ''
        if 'protocolParam' not in raw:
            raw['protocolParam'] = ''
        if 'obfs' not in raw:
            raw['obfs'] = ''
        if 'obfsParam' not in raw:
            raw['obfsParam'] = ''
    except:
        pass
    return raw

def __ssrFormat(raw: dict) -> dict: # 容错性格式化
    try:
        raw['server'] = raw['server'].strip()
        raw['port'] = int(raw['port'])
        raw['method'] = raw['method'].replace('_', '-').lower().strip()
        if raw['protocol'] is None:
            raw['protocol'] = ''
        if raw['protocolParam'] is None:
            raw['protocolParam'] = ''
        if raw['obfs'] is None:
            raw['obfs'] = ''
        if raw['obfsParam'] is None:
            raw['obfsParam'] = ''
        raw['protocol'] = raw['protocol'].replace('-', '_').lower().strip()
        raw['obfs'] = raw['obfs'].replace('-', '_').lower().strip()
    except:
        pass
    return raw

def __ssrParamCheck(raw: dict) -> tuple[bool, str or None]: # 参数检查
    try:
        if 'server' not in raw:
            return False, 'Missing `server` option'
        if 'port' not in raw:
            return False, 'Missing `port` option'
        if 'method' not in raw:
            return False, 'Missing `method` option'
        if 'passwd' not in raw:
            return False, 'Missing `passwd` option'
        if 'protocol' not in raw:
            return False, 'Missing `protocol` option'
        if 'protocolParam' not in raw:
            return False, 'Missing `protocolParam` option'
        if 'obfs' not in raw:
            return False, 'Missing `obfs` option'
        if 'obfsParam' not in raw:
            return False, 'Missing `obfsParam` option'

        if not isinstance(raw['server'], str):
            return False, 'Illegal `server` option'
        if not isinstance(raw['port'], int):
            return False, 'Illegal `int` option'
        if not isinstance(raw['method'], str):
            return False, 'Illegal `method` option'
        if not isinstance(raw['passwd'], str):
            return False, 'Illegal `passwd` option'
        if not isinstance(raw['protocol'], str):
            return False, 'Illegal `protocol` option'
        if not isinstance(raw['protocolParam'], str):
            return False, 'Illegal `protocolParam` option'
        if not isinstance(raw['obfs'], str):
            return False, 'Illegal `obfs` option'
        if not isinstance(raw['obfsParam'], str):
            return False, 'Illegal `obfsParam` option'
    except:
        return False, 'Unknown error'
    return True, None

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
        raw = rawInfo
        raw = __ssrFormat(__ssrFill(raw))  # 预处理
        status, reason = __ssrParamCheck(raw) # 参数检查
        if not status: # 参数有误
            return False, reason

        result = {'type': 'ssr'}
        if isExtra: # 携带额外参数
            if 'remark' not in raw: # 补全默认值
                raw['remark'] = ''
            if 'group' not in raw:
                raw['group'] = ''
            if raw['remark'] is None: # 容错格式化
                raw['remark'] = ''
            if raw['group'] is None:
                raw['group'] = ''
            if not isinstance(raw['remark'], str): # 参数检查
                return False, 'Illegal `remark` option'
            if not isinstance(raw['group'], str):
                return False, 'Illegal `group` option'
            result['remark'] = raw['remark']
            result['group'] = raw['group']

        if baseFunc.isHost(raw['server']):
            result['server'] = raw['server'] # server
        else:
            return False, 'Illegal `server` option'
        if baseFunc.isPort(raw['port']):
            result['port'] = raw['port'] # port
        else:
            return False, 'Illegal `port` option'
        if raw['method'] in ssrMethodList:
            result['method'] = raw['method'] # method
        else:
            return False, 'Unknown ShadowsocksR method'
        result['passwd'] = raw['passwd'] # passwd

        if raw['protocol'] in ['', 'origin']: # 默认协议
            result['protocol'] = 'origin'
            result['protocolParam'] = ''
        else:
            if raw['protocol'] in ssrProtocolList:
                result['protocol'] = raw['protocol']
                result['protocolParam'] = raw['protocolParam']
            else:
                return False, 'Unknown ShadowsocksR protocol'

        if raw['obfs'] in ['', 'plain']: # 默认混淆
            result['obfs'] = 'plain'
            result['obfsParam'] = ''
        else:
            if raw['obfs'] in ssrObfsList:
                result['obfs'] = raw['obfs']
                result['obfsParam'] = raw['obfsParam']
            else:
                return False, 'Unknown ShadowsocksR obfs'
    except:
        return False, 'Unknown error'
    return True, result
