#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import V2ray

vmessMethodList = [
    'aes-128-gcm',
    'chacha20-poly1305',
    'auto',
    'none',
    'zero',
]

vmessFilterRules = {
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
            'default': 'auto',
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
            'filter': lambda method: method in vmessMethodList,
            'errMsg': 'Unknown VMess method'
        },
        'id': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'aid': {
            'optional': False,
            'default': 0,
            'type': int,
            'format': baseFunc.toInt,
            'filter': lambda aid: aid in range(0, 65536), # 0 ~ 65535
            'errMsg': 'Illegal alter Id'
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

def vmessFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    VMess节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'vmess',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            vmessFilterRules['rootObject'].pop('remark')
        for key, obj in V2ray.v2rayStreamRules.items(): # v2ray.stream -> vmess
            vmessFilterRules[key] = obj
        status, result = baseFunc.ruleFilter(rawInfo, vmessFilterRules, {
            'type': 'vmess'
        })
        if not status: # 节点格式错误
            return False, result
        V2ray.addSni(result)
        return True, result
    except:
        return False, 'Unknown error'
