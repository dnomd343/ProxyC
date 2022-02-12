#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

ssrMethodList = [
    "aes-128-cfb",
    "aes-192-cfb",
    "aes-256-cfb",
    "aes-128-cfb1",
    "aes-192-cfb1",
    "aes-256-cfb1",
    "aes-128-cfb8",
    "aes-192-cfb8",
    "aes-256-cfb8",
    "aes-128-ctr",
    "aes-192-ctr",
    "aes-256-ctr",
    "aes-128-gcm",
    "aes-192-gcm",
    "aes-256-gcm",
    "aes-128-ofb",
    "aes-192-ofb",
    "aes-256-ofb",
    "camellia-128-cfb",
    "camellia-192-cfb",
    "camellia-256-cfb",
    "none",
    "table",
    "rc4",
    "rc4-md5",
    "rc4-md5-6",
    "bf-cfb",
    "cast5-cfb",
    "des-cfb",
    "idea-cfb",
    "seed-cfb",
    "rc2-cfb",
    "salsa20",
    "xsalsa20",
    "chacha20",
    "xchacha20",
    "chacha20-ietf",
]

ssrProtocolList = [
    "origin",
    "verify_sha1",
    "verify_simple",
    "verify_deflate",
    "auth_simple",
    "auth_sha1",
    "auth_sha1_v2",
    "auth_sha1_v4",
    "auth_aes128",
    "auth_aes128_md5",
    "auth_aes128_sha1",
    "auth_chain_a",
    "auth_chain_b",
    "auth_chain_c",
    "auth_chain_d",
    "auth_chain_e",
    "auth_chain_f",
]

ssrObfsList = [
    "plain",
    "http_post",
    "http_simple",
    "tls_simple",
    "tls1.2_ticket_auth",
    "tls1.2_ticket_fastauth",
    "random_head",
]

def __ssrFormat(raw): # 容错性格式化
    try:
        raw['server'] = raw['server'].strip()
        raw['port'] = int(raw['port'])
        raw['method'] = raw['method'].replace('_', '-').lower().strip()
        if 'protocol' in raw:
            raw['protocol'] = raw['protocol'].replace('-', '_').lower().strip()
        if 'obfs' in raw:
            raw['obfs'] = raw['obfs'].replace('-', '_').lower().strip()
    except:
        pass
    return raw


def ssrFilter(raw):
    '''
    ShadowsocksR节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'ssr',
                'server': '...',
                'port': ...,
                'password': '...',
                'method": '...',
                'protocol': '...',
                'protocolParam': '...',
                'obfs': '...',
                'obfsParam': '...'
            }
    '''
    try:
        result = {}
        result['type'] = 'ssr'
        raw = __ssrFormat(raw)

        if not 'server' in raw:
            return False, 'Missing `server` option'
        if not 'port' in raw:
            return False, 'Missing `port` option'
        if not 'password' in raw:
            return False, 'Missing `password` option'
        if not 'method' in raw:
            return False, 'Missing `method` option'

        if baseFunc.isHost(raw['server']):
            result['server'] = raw['server']
        else:
            return False, 'Illegal `server` option'
        if baseFunc.isPort(raw['port']):
            result['port'] = raw['port']
        else:
            return False, 'Illegal `port` option'
        result['password'] = raw['password']
        if raw['method'] in ssrMethodList:
            result['method'] = raw['method']
        else:
            return False, 'Unknown ShadowsocksR method'

        if (not 'protocol' in raw) or raw['protocol'] == 'origin' or raw['protocol'] == '':
            result['protocol'] = 'origin'
            result['protocolParam'] = ''
        else:
            if raw['protocol'] in ssrProtocolList:
                result['protocol'] = raw['protocol']
                result['protocolParam'] = raw['protocolParam']
            else:
                return False, 'Unknown ShadowsocksR protocol'

        if (not 'obfs' in raw) or raw['obfs'] == 'plain' or raw['obfs'] == '':
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
