#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Utils.Common import isHost, isPort
from Utils.Filter import Filter, rulesFilter
from Utils.Common import toInt, toStr, toStrTidy, hostFormat
from Utils.Constant import ssrMethods, ssrProtocols, ssrObfuscations


def ssrProtocolFormat(protocol: str) -> str:
    protocol = toStr(protocol).strip().lower().replace('-', '_')
    return 'origin' if protocol == '' else protocol  # '' -> origin


def ssrObfsFormat(obfs: str) -> str:
    obfs = toStr(obfs).strip().lower().replace('-', '_')
    return 'plain' if obfs == '' else obfs  # '' -> plain


ssrObject = rulesFilter({
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
    'method': {
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in ssrMethods,
        'errMsg': 'Unknown ShadowsocksR method'
    },
    'passwd': {
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
    },
    'protocol': {
        'optional': True,
        'default': 'origin',
        'type': str,
        'format': ssrProtocolFormat,
        'filter': lambda s: s in ssrProtocols,
        'errMsg': 'Unknown ShadowsocksR protocol'
    },
    'protocolParam': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid ShadowsocksR protocol param'
    },
    'obfs': {
        'optional': True,
        'default': 'plain',
        'type': str,
        'format': ssrObfsFormat,
        'filter': lambda s: s in ssrObfuscations,
        'errMsg': 'Unknown ShadowsocksR obfuscation'
    },
    'obfsParam': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid ShadowsocksR obfuscation param'
    }
})


def ssrFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    proxyInfo = Filter(proxyInfo, ssrObject)  # run filter
    if proxyInfo['protocol'] == 'origin':  # origin without param
        proxyInfo['protocolParam'] = ''
    if proxyInfo['obfs'] == 'plain':  # plain without param
        proxyInfo['obfsParam'] = ''
    return proxyInfo
