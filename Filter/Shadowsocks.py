#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Filter.Plugin import pluginObject
from Basis.Constant import ssAllMethods
from Basis.Functions import isHost, isPort
from Basis.Filter import Filter, rulesFilter
from Basis.Functions import toInt, toStr, toStrTidy

ssObject = rulesFilter({
    'server': {
        'type': str,
        'format': toStrTidy,
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
        'format': lambda s: toStrTidy(s).replace('_', '-'),
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
        'errMsg': 'Invalid plugin options'
    }
})


def ssFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    return Filter(proxyInfo, ssObject)  # run filter
