#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Filter import V2ray
from Utils.Constant import vmessMethods
from Utils.Common import isHost, isPort
from Utils.Common import toInt, toStrTidy
from Utils.Filter import Filter, rulesFilter

vmessObject = rulesFilter({
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
        'default': 'auto',
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in vmessMethods,
        'errMsg': 'Unknown VMess method'
    },
    'id': {
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid VMess ID'
    },
    'aid': {
        'optional': True,
        'default': 0,
        'type': int,
        'format': toInt,
        'filter': lambda i: i in range(0, 65536),  # 0 ~ 65535
        'errMsg': 'Invalid VMess alter ID'
    },
    'stream': {
        'optional': True,
        'default': {
            'type': 'tcp'
        },
        'multiSub': True,
        'type': {
            'tcp': V2ray.tcpObject,
            'kcp': V2ray.kcpObject,
            'ws': V2ray.wsObject,
            'h2': V2ray.h2Object,
            'quic': V2ray.quicObject,
            'grpc': V2ray.grpcObject,
        },
        'errMsg': 'Invalid VMess stream'
    }
})


def vmessFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    proxyInfo = Filter(proxyInfo, vmessObject)  # run filter
    V2ray.addSni(proxyInfo)  # add SNI option
    return proxyInfo
