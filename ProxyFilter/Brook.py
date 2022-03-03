#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

brookFilterRules = {
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
        'ws': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'wsObject'
        }
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
        },
        'secure': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'secureObject'
        }
    },
    'secureObject': {
        'verify': {
            'optional': False,
            'default': True,
            'type': bool,
            'format': baseFunc.toBool
        }
    }
}

def brookFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    Brook节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'brook',
                ...
            }
    """
    try:
        if not isExtra: # 去除非必要参数
            brookFilterRules['rootObject'].pop('remark')
        status, result = baseFunc.ruleFilter(rawInfo, brookFilterRules, {
            'type': 'brook'
        })
        if not status: # 节点格式错误
            return False, result
        if result['ws'] is not None and result['ws']['host'] == '':
            result['ws']['host'] = result['server']
        return True, result
    except:
        return False, 'Unknown error'
