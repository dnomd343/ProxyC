#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Filter import Xray
from Basis.Filter import rulesFilter
from Basis.Functions import isHost, isPort
from Basis.Functions import toInt, toStr, toStrTidy

trojanObject = rulesFilter({
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
    'passwd': {
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
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
        'errMsg': 'Invalid Trojan stream'
    }
})
