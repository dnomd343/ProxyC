#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Filter.Plugin import pluginObject
from Utils.Constant import trojanGoMethods
from Utils.Filter import Filter, rulesFilter
from Utils.Common import isHost, isPort, hostFormat
from Utils.Common import isIpAddr, toInt, toStr, toStrTidy, toBool

ssObject = rulesFilter({
    'method': {
        'optional': True,
        'default': 'aes-128-gcm',
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in trojanGoMethods,
        'errMsg': 'Unknown Shadowsocks method'
    },
    'passwd': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid Shadowsocks password'
    }
})

wsObject = rulesFilter({
    'host': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid WebSocket host'
    },
    'path': {
        'optional': True,
        'default': '/',
        'type': str,
        'format': lambda s: toStr(s).strip(),
        'errMsg': 'Invalid WebSocket path'
    }
})

trojanGoObject = rulesFilter({
    'server': {
        'type': str,
        'format': lambda s: hostFormat(toStrTidy(s)),
        'filter': isHost,
        'errMsg': 'Invalid server address'
    },
    'port': {
        'type': int,
        'format': toInt,
        'filter': isPort,
        'errMsg': 'Invalid port number'
    },
    'passwd': {
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
    },
    'sni': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid SNI content'
    },
    'alpn': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': lambda s: toStrTidy(s).replace(' ', ''),  # remove space
        'filter': lambda s: s in ['h2', 'http/1.1', 'h2,http/1.1'],
        'errMsg': 'Invalid alpn option'
    },
    'verify': {
        'optional': True,
        'default': True,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid verify option'
    },
    'ws': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': wsObject,
        'errMsg': 'Invalid WebSocket options'
    },
    'ss': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': ssObject,
        'errMsg': 'Invalid Shadowsocks options'
    },
    'plugin': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': pluginObject,
        'errMsg': 'Invalid plugin options'
    }
})


def trojanGoFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    proxyInfo = Filter(proxyInfo, trojanGoObject)  # run filter
    if proxyInfo['sni'] == '' and not isIpAddr(proxyInfo['server']):
        proxyInfo['sni'] = proxyInfo['server']
    return proxyInfo
