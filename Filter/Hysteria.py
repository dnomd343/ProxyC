#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Utils.Constant import hysteriaProtocols
from Utils.Filter import Filter, rulesFilter
from Utils.Common import isHost, isPort, isIpAddr
from Utils.Common import toInt, toStr, toStrTidy, toBool

hysteriaObject = rulesFilter({
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
    'protocol': {
        'optional': True,
        'default': 'udp',
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in hysteriaProtocols,
        'errMsg': 'Unknown Hysteria protocol'
    },

    'obfs': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid obfs content'
    },
    'passwd': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
    },

    'up': {
        'optional': True,
        'default': 10,
        'type': int,
        'format': toInt,
        'filter': lambda i: i > 0,
        'errMsg': 'Invalid upload speed option'
    },
    'down': {
        'optional': True,
        'default': 50,
        'type': int,
        'format': toInt,
        'filter': lambda i: i > 0,
        'errMsg': 'Invalid download speed option'
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
        'format': toStrTidy,
        'errMsg': 'Invalid alpn option'
    },
    'verify': {
        'optional': True,
        'default': True,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid verify option'
    }
})


def hysteriaFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    proxyInfo = Filter(proxyInfo, hysteriaObject)  # run filter
    if proxyInfo['sni'] == '' and not isIpAddr(proxyInfo['server']):
        proxyInfo['sni'] = proxyInfo['server']
    return proxyInfo
