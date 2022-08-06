#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis.Filter import rulesFilter
from Filter.Plugin import pluginObject
from Basis.Constant import ssAllMethods
from Basis.Functions import toInt, toStr
from Basis.Functions import isHost, isPort

ssObject = rulesFilter({
    'server': {
        'type': str,
        'format': lambda s: toStr(s).strip().lower(),
        'filter': isHost,
        'errMsg': 'Invalid server address'
    },
    'port': {
        'type': int,
        'format': toInt,
        'filter': isPort,
        'errMsg': 'Invalid port number'
    },
    'method': {
        'type': str,
        'format': lambda s: toStr(s).strip().lower().replace('_', '-'),
        'filter': lambda s: s in ssAllMethods,
        'errMsg': 'Unknown Shadowsocks method'
    },
    'passwd': {
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
    },
    'plugin': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': pluginObject,
        'errMsg': 'Invalid pluginObject'
    }
})
