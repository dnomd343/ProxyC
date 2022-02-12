#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import Plugin as sip003

ssMethodList = [
    'aes-128-gcm',
    'aes-192-gcm',
    'aes-256-gcm',
    'aes-128-ctr',
    'aes-192-ctr',
    'aes-256-ctr',
    'aes-128-ocb',
    'aes-192-ocb',
    'aes-256-ocb',
    'aes-128-ofb',
    'aes-192-ofb',
    'aes-256-ofb',
    'aes-128-cfb',
    'aes-192-cfb',
    'aes-256-cfb',
    'aes-128-cfb1',
    'aes-192-cfb1',
    'aes-256-cfb1',
    'aes-128-cfb8',
    'aes-192-cfb8',
    'aes-256-cfb8',
    'aes-128-cfb128',
    'aes-192-cfb128',
    'aes-256-cfb128',
    'camellia-128-cfb',
    'camellia-192-cfb',
    'camellia-256-cfb',
    'camellia-128-cfb128',
    'camellia-192-cfb128',
    'camellia-256-cfb128',
    'plain',
    'none',
    'table',
    'rc4',
    'rc4-md5',
    'rc2-cfb',
    'bf-cfb',
    'cast5-cfb',
    'des-cfb',
    'idea-cfb',
    'seed-cfb',
    'salsa20',
    'salsa20-ctr',
    'xchacha20',
    'chacha20',
    'chacha20-ietf',
    'chacha20-poly1305',
    'chacha20-ietf-poly1305',
    'xchacha20-ietf-poly1305'
]

pluginList = [
    'obfs-local',
    'simple-tls',
    'v2ray-plugin',
    'xray-plugin',
    'kcptun-client',
    'gost-plugin',
    'ck-client',
    'gq-client',
    'mtt-client',
    'rabbit-plugin',
    'qtun-client',
    'gun-plugin'
]

def __ssFormat(raw): # 容错性格式化
    try:
        raw['server'] = raw['server'].strip()
        raw['port'] = int(raw['port'])
        raw['method'] = raw['method'].replace('_', '-').lower().strip()
        raw['plugin'] = sip003.pluginFormat(raw['plugin'])
    except:
        pass
    return raw

def ssFilter(raw):
    '''
    Shadowsocks节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'ss',
                'server': '...',
                'port': ...,
                'password': '...',
                'method": '...',
                'plugin": '...',
                'pluginParam": '...'
            }
    '''
    try:
        result = {}
        result['type'] = 'ss'
        raw = __ssFormat(raw)

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
        if raw['method'] in ssMethodList:
            result['method'] = raw['method']
        else:
            return False, 'Unknown Shadowsocks method'

        if (not 'plugin' in raw) or raw['plugin'] == '':
            result['plugin'] = ''
            result['pluginParam'] = ''
        else:
            if raw['plugin'] in pluginList:
                result['plugin'] = raw['plugin']
                result['pluginParam'] = raw['pluginParam']
            else:
                return False, 'Unknown sip003 plugin'
    except:
        return False, 'Unknown error'
    return True, result
