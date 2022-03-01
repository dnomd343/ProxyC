#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import Xray

vlessMethodList = ['none']

vlessFilterRules = {
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
            'optional': False,
            'default': 'none',
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': lambda method: method in vlessMethodList,
            'errMsg': 'Unknown VLESS method'
        },
        'id': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'stream': {
            'optional': False,
            'default': {
                'type': 'tcp'
            },
            'type': [
                'tcpObject',
                'kcpObject',
                'wsObject',
                'h2Object',
                'quicObject',
                'grpcObject',
            ]
        }
    }
}

def vlessFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    VLESS节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'vless',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            vlessFilterRules['rootObject'].pop('remark')
        for key, obj in Xray.xrayStreamRules.items(): # xray.stream -> vless
            vlessFilterRules[key] = obj
        status, result = baseFunc.ruleFilter(rawInfo, vlessFilterRules, {
            'type': 'vless'
        })
        if not status: # 节点格式错误
            return False, result
        Xray.addSni(result)
        return True, result
    except:
        return False, 'Unknown error'
