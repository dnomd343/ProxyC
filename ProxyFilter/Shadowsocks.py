#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import Plugin as sip003

ssMethodList = [ # Shadowsocks加密方式
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

pluginList = [ # SIP003插件列表
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

def __ssFill(raw: dict) -> dict: # 补全可选值
    try:
        if 'plugin' not in raw:
            raw['plugin'] = None
        if raw['plugin'] is not None:
            if 'type' not in raw['plugin']:
                raw['plugin']['type'] = ''
            if 'param' not in raw['plugin']:
                raw['plugin']['param'] = ''
    except:
        pass
    return raw

def __ssFormat(raw: dict) -> dict: # 容错性格式化
    try:
        raw['server'] = raw['server'].strip()
        raw['port'] = int(raw['port'])
        raw['method'] = raw['method'].replace('_', '-').lower().strip()
        if raw['plugin'] is not None:
            raw['plugin']['type'] = sip003.pluginFormat(raw['plugin']['type'])
    except:
        pass
    return raw

def ssFilter(raw: dict) -> tuple[bool, str or dict]:
    """
    Shadowsocks节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'ss',
                ...
            }
    """
    try:
        if 'server' not in raw: # 必选值检查
            return False, 'Missing `server` option'
        if 'port' not in raw:
            return False, 'Missing `port` option'
        if 'method' not in raw:
            return False, 'Missing `method` option'
        if 'passwd' not in raw:
            return False, 'Missing `passwd` option'
        raw = __ssFormat(__ssFill(raw)) # 预处理

        result = {'type': 'ss'}
        if baseFunc.isHost(raw['server']):
            result['server'] = raw['server'] # server
        else:
            return False, 'Illegal `server` option'
        if baseFunc.isPort(raw['port']):
            result['port'] = raw['port'] # port
        else:
            return False, 'Illegal `port` option'
        if raw['method'] in ssMethodList:
            result['method'] = raw['method'] # method
        else:
            return False, 'Unknown Shadowsocks method'
        result['passwd'] = raw['passwd'] # passwd

        if raw['plugin'] is None or raw['plugin']['type'] in [None, '']:
            plugin = None
        else:
            if raw['plugin']['type'] in pluginList:
                plugin = {
                    'type': raw['plugin']['type'],
                    'param': raw['plugin']['param']
                }
            else:
                return False, 'Unknown sip003 plugin'
        result['plugin'] = plugin
    except:
        return False, 'Unknown error'
    return True, result
