#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import Xray

trojanFilterRules = {
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

def trojanFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    Trojan节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'trojan',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            trojanFilterRules['rootObject'].pop('remark')
        for key, obj in Xray.xrayStreamRules.items(): # xray.stream -> trojan
            trojanFilterRules[key] = obj
        status, result = baseFunc.ruleFilter(rawInfo, trojanFilterRules, {
            'type': 'trojan'
        })
        if not status: # 节点格式错误
            return False, result
        stream = result['stream']
        if stream['secure'] is not None and stream['secure']['sni'] == '': # 未指定SNI
            if stream['type'] == 'tcp' and stream['obfs'] is not None:
                stream['secure']['sni'] = stream['obfs']['host'].split(',')[0]
            elif stream['type'] == 'ws':
                stream['secure']['sni'] = stream['host']
            elif stream['type'] == 'h2':
                stream['secure']['sni'] = stream['host'].split(',')[0]
        return True, result
    except:
        return False, 'Unknown error'
