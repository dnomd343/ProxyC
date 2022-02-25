#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc
from ProxyFilter import V2ray

xrayFlowList = [
    'xtls-origin',
    'xtls-direct',
    'xtls-splice',
]

def testFunc(raw):
    print(raw)
    return False

xrayStreamRules = V2ray.v2rayStreamRules
xrayStreamRules.pop('secureObject')
xrayStreamRules['tcpObject']['secure']['type'] = ['tlsObject', 'xtlsObject']
xrayStreamRules['kcpObject']['secure']['type'] = ['tlsObject', 'xtlsObject']
xrayStreamRules['wsObject']['secure']['type'] = 'tlsObject'
xrayStreamRules['h2Object']['secure']['type'] = 'tlsObject'
xrayStreamRules['quicObject']['secure']['type'] = 'tlsObject'
xrayStreamRules['grpcObject']['secure']['type'] = 'tlsObject'

xrayStreamRules['tlsObject'] = {
    'type': {
        'optional': True,
        'type': str,
        'indexKey': True,
        'format': baseFunc.toStrTidy,
        'filter': lambda secureType: secureType == 'tls',
        'errMsg': 'Unexpected secure type'
    },
    'sni': {
        'optional': False,
        'default': '',
        'type': str,
        'format': baseFunc.toStr
    },
    'alpn': {
        'optional': False,
        'default': 'h2,http/1.1',
        'type': str,
        'format': baseFunc.toStrTidy,
        'filter': lambda alpn: alpn in ['h2', 'http/1.1', 'h2,http/1.1'],
        'errMsg': 'Illegal alpn option'
    },
    'verify': {
        'optional': False,
        'default': True,
        'type': bool,
        'format': baseFunc.toBool
    }
}

xrayStreamRules['xtlsObject'] = {
    'type': {
        'optional': True,
        'type': str,
        'indexKey': True,
        'format': baseFunc.toStrTidy,
        'filter': lambda secureType: secureType == 'xtls',
        'errMsg': 'Unexpected secure type'
    },
    'sni': {
        'optional': False,
        'default': '',
        'type': str,
        'format': baseFunc.toStr
    },
    'alpn': {
        'optional': False,
        'default': 'h2,http/1.1',
        'type': str,
        'format': baseFunc.toStrTidy,
        'filter': lambda alpn: alpn in ['h2', 'http/1.1', 'h2,http/1.1'],
        'errMsg': 'Illegal alpn option'
    },
    'verify': {
        'optional': False,
        'default': True,
        'type': bool,
        'format': baseFunc.toBool
    },
    'flow': {
        'optional': False,
        'default': 'xtls-direct',
        'type': str,
        'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
        'filter': lambda flow: flow in xrayFlowList,
        'errMsg': 'Unknown XTLS flow method'
    },
    'udp443': {
        'optional': False,
        'default': False,
        'type': bool,
        'format': baseFunc.toBool
    }
}
