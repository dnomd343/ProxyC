#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Filter import Xray
from Basis.Functions import isHost, isPort
from Basis.Filter import Filter, rulesFilter
from Basis.Functions import toInt, toStrTidy

vlessObject = rulesFilter({
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
        'optional': True,
        'default': 'none',
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'none',
        'errMsg': 'Unknown VLESS method'
    },
    'id': {
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid VLESS ID'
    },
    'stream': {
        'optional': True,
        'default': {
            'type': 'tcp'
        },
        'multiSub': True,
        'type': {
            'tcp': Xray.tcpObject,
            'kcp': Xray.kcpObject,
            'ws': Xray.wsObject,
            'h2': Xray.h2Object,
            'quic': Xray.quicObject,
            'grpc': Xray.grpcObject,
        },
        'errMsg': 'Invalid VLESS stream'
    }
})


def vlessFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    proxyInfo = Filter(proxyInfo, vlessObject)  # run filter
    Xray.addSni(proxyInfo)  # add SNI option
    return proxyInfo
