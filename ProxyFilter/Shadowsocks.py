#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import Plugin
from ProxyFilter import baseFunc

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

ssFilterRules = {
    'rootObject': {
        'remark': {
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
            'filter': lambda method: method in ssMethodList,
            'errMsg': 'Unknown Shadowsocks method'
        },
        'passwd': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'plugin': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'pluginObject'
        }
    },
    'pluginObject': {
        'type': {
            'optional': True,
            'type': str,
            'format': lambda pluginType: Plugin.pluginFormat(baseFunc.toStrTidy(pluginType)),
            'filter': Plugin.isPlugin,
            'errMsg': 'Unknown SIP003 plugin'
        },
        'param': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        }
    }
}

def ssFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
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
        if not isExtra: # 去除非必要参数
            ssFilterRules['rootObject'].pop('remark')
        return baseFunc.ruleFilter(rawInfo, ssFilterRules, {
            'type': 'ss'
        })
    except:
        return False, 'Unknown error'
