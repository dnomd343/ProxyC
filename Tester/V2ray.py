#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import itertools
from Basis.Test import Settings
from Basis.Functions import genFlag
from Basis.Constant import quicMethods, udpObfuscations

httpConfig = {
    'version': '1.1',
    'status': '200',
    'reason': 'OK',
    'headers': {
        'Content-Type': [
            'application/octet-stream',
            'video/mpeg'
        ],
        'Transfer-Encoding': ['chunked'],
        'Connection': ['keep-alive'],
        'Pragma': 'no-cache',
    }
}

kcpConfig = {
    'mtu': 1350,
    'tti': 20,
    'uplinkCapacity': 5,
    'downlinkCapacity': 20,
    'congestion': False,
    'readBufferSize': 1,
    'writeBufferSize': 1,
}


def addSecure(streamConfig: dict) -> dict:
    streamConfig['caption'] += ' (with tls)'
    streamConfig['info']['secure'] = {  # secure options for client
        'sni': Settings['host'],
        'alpn': None,
        'verify': True,
    }
    streamConfig['server']['security'] = 'tls'
    streamConfig['server']['tlsSettings'] = {  # cert and key for server
        'alpn': ['h2', 'http/1.1'],
        'certificates': [{
            'certificateFile': Settings['cert'],
            'keyFile': Settings['key'],
        }]
    }
    return streamConfig


def tcpStream(isObfs: bool) -> dict:
    return {
        'caption': 'TCP stream' + (' (with obfs)' if isObfs else ''),
        'info': {
            'type': 'tcp',
            'obfs': None if not isObfs else {
                'host': Settings['site'],  # obfs website
                'path': '/',
            },
            'secure': None,
        },
        'server': {
            'network': 'tcp',
            'tcpSettings': {} if not isObfs else {
                'header': {
                    'type': 'http',
                    'response': httpConfig,
                }
            }
        }
    }


def kcpStream(obfs: str) -> dict:
    kcpObject = copy.deepcopy(kcpConfig)
    kcpObject['seed'] = genFlag(length = 8)  # random seed
    kcpObject['header'] = {
        'type': obfs
    }
    return {
        'caption': 'mKCP stream obfs ' + obfs,
        'info': {
            'type': 'kcp',
            'seed': kcpObject['seed'],
            'obfs': obfs,
            'secure': None
        },
        'server': {
            'network': 'kcp',
            'kcpSettings': kcpObject
        }
    }


def wsStream(isEd: bool) -> dict:
    path = '/' + genFlag(length = 6)  # random websocket path
    return {
        'caption': 'WebSocket stream' + (' (Max-Early-Data 2048)' if isEd else ''),
        'info': {
            'type': 'ws',
            'host': Settings['host'],
            'path': path,
            'ed': 2048 if isEd else None,
            'secure': None,
        },
        'server': {
            'network': 'ws',
            'wsSettings': {
                'path': path,
                'headers': {
                    'Host': Settings['host']
                },
                **({} if not isEd else {
                    'maxEarlyData': 2048,
                    'earlyDataHeaderName': 'Sec-WebSocket-Protocol'
                })
            }
        }
    }


def h2Stream() -> dict:
    path = '/' + genFlag(length = 6)
    return {
        'caption': 'HTTP/2 stream',
        'info': {
            'type': 'h2',
            'host': Settings['host'],
            'path': path,
            'secure': None,  # HTTP/2 stream force enable tls
        },
        'server': {
            'network': 'http',
            'httpSettings': {
                'host': [Settings['host']],
                'path': path
            }
        }
    }


def quicStream(method: str, obfs: str) -> dict:
    passwd = genFlag(length = 8)
    return {
        'caption': 'QUIC stream security = %s | header = %s' % (method, obfs),
        'info': {
            'type': 'quic',
            'method': method,
            'passwd': passwd,
            'obfs': obfs,
            'secure': None,  # QUIC stream force enable tls
        },
        'server': {
            'network': 'quic',
            'quicSettings': {
                'security': method,
                'key': passwd,
                'header': {
                    'type': obfs
                }
            }
        }
    }


def grpcStream(isMulti: bool) -> dict:
    service = genFlag(length = 8)
    return {
        'caption': 'gRPC stream' + (' (multi mode)' if isMulti else ''),
        'info': {
            'type': 'grpc',
            'service': service,
            'mode': 'multi' if isMulti else 'gun',  # gun mode or multi mode
            'secure': None,
        },
        'server': {
            'network': 'grpc',
            'grpcSettings': {
                'serviceName': service,
                **({} if not isMulti else {
                    'multiMode': True
                })
            }
        }
    }


def loadStream() -> list:
    streams = []
    addStream = lambda x: streams.append(copy.deepcopy(x))
    for isObfs in [False, True]:
        addStream(tcpStream(isObfs))  # TCP stream
        addStream(addSecure(tcpStream(isObfs)))  # TCP stream with TLS
    for udpObfs in udpObfuscations:
        addStream(kcpStream(udpObfs))  # mKCP stream
        addStream(addSecure(kcpStream(udpObfs)))  # mKCP stream with TLS
    for isEd in [False, True]:
        addStream(wsStream(isEd))  # WebSocket stream
        addStream(addSecure(wsStream(isEd)))  # WebSocket stream with TLS
    addStream(addSecure(h2Stream()))  # HTTP/2 stream with TLS
    for quicMethod, quicObfs in itertools.product(quicMethods, udpObfuscations):
        addStream(addSecure(quicStream(quicMethod, quicObfs)))  # QUIC stream with TLS
    for isMulti in [False, True]:
        addStream(grpcStream(isMulti))  # gRPC stream
        addStream(addSecure(grpcStream(isMulti)))  # gRPC stream with TLS
    return streams


def loadConfig(inbound: dict) -> dict:
    return {
        'log': {
            'loglevel': 'debug'
        },
        'inbounds': [inbound],
        'outbounds': [{
            'protocol': 'freedom',
            'settings': {},
        }]
    }
