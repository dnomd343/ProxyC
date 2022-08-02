#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

hysteriaFilterRules = {
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
            'format': baseFunc.toHost,
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
        'protocol': {
            'optional': False,
            'default': 'udp',
            'type': str,
            'format': baseFunc.toStr,
            'filter': lambda protocol: protocol in ['udp', 'wechat-video', 'faketcp'],
            'errMsg': 'Unknown Hysteria protocol'
        },
        'obfs': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'auth': {
            'optional': False,
            'default': None,
            'allowNone': True,
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
            'format': baseFunc.toStr
        },
        'verify': {
            'optional': False,
            'default': True,
            'type': bool,
            'format': baseFunc.toBool
        }
    }
}

def filte(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    Hysteria节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'hysteria',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            hysteriaFilterRules['rootObject'].pop('remark')
        return baseFunc.ruleFilter(rawInfo, hysteriaFilterRules, {})
    except:
        return False, 'Unknown error'
