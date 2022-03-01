#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import Plugin

trojanGoFilterRules = {
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
        'passwd': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'sni': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'alpn': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': lambda alpn: alpn in ['h2', 'http/1.1', 'h2,http/1.1'],
            'errMsg': 'Illegal alpn option'
        },
        'verify': {
            'optional': False,
            'default': True,
            'type': bool,
            'format': baseFunc.toBool
        },
        'ws': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'wsObject'
        },
        'ss': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'ssObject'
        },
        'plugin': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'pluginObject'
        }
    },
    'ssObject': {
        'method': {
            'optional': False,
            'default': 'AES-128-GCM',
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-').upper(),
            'filter': lambda method: method in ['AES-128-GCM', 'AES-256-GCM', 'CHACHA20-IETF-POLY1305'],
            'errMsg': 'Unknown Shadowsocks method'
        },
        'passwd': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
    },
    'wsObject': {
        'host': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str,
            'format': baseFunc.toStr
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

def trojanGoFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    Trojan-Go节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'trojan-go',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            trojanGoFilterRules['rootObject'].pop('remark')
        return baseFunc.ruleFilter(rawInfo, trojanGoFilterRules, {
            'type': 'trojan-go'
        })
    except:
        return False, 'Unknown error'
