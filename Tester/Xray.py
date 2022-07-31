#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import itertools
from Tester import V2ray
from Tester import Settings
from Basis.Methods import xtlsFlows
from Basis.Functions import genFlag
from Basis.Methods import quicMethods
from Basis.Methods import udpObfuscations

loadConfig = V2ray.loadConfig
tcpStream = V2ray.tcpStream
kcpStream = V2ray.kcpStream
h2Stream = V2ray.h2Stream
quicStream = V2ray.quicStream
grpcStream = V2ray.grpcStream


def addSecure(streamConfig: dict, xtlsFlow: str or None = None, isUdp443: bool = False) -> dict:  # add TLS or XTLS
    streamConfig['caption'] += ' (with %s)' % (
        'tls' if xtlsFlow is None else (xtlsFlow + ('-udp443' if isUdp443 else ''))
    )
    streamConfig['info']['secure'] = {**{  # secure options for client
        'type': 'tls' if xtlsFlow is None else 'xtls',
        'sni': Settings['host'],
        'alpn': None,
        'verify': True,
    }, **({} if xtlsFlow is None else {
        'flow': xtlsFlow,
        'udp443': isUdp443,
    })}
    streamConfig['server']['security'] = 'tls' if xtlsFlow is None else 'xtls'
    streamConfig['server']['%sSettings' % streamConfig['server']['security']] = {  # cert and key for server
        'alpn': ['h2', 'http/1.1'],
        'certificates': [{
            'certificateFile': Settings['cert'],
            'keyFile': Settings['key'],
        }]
    }
    return streamConfig


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
                'path': path + ('?ed=2048' if isEd else ''),
                'headers': {
                    'Host': Settings['host']
                }
            }
        }
    }


def loadStream() -> list:
    streams = []
    addStream = lambda x: streams.append(copy.deepcopy(x))
    for isObfs in [False, True]:
        addStream(tcpStream(isObfs))  # TCP stream
        addStream(addSecure(tcpStream(isObfs)))  # TCP stream with TLS
        if isObfs: continue  # can't use XTLS when enable obfs
        for xtlsFlow, udp443 in itertools.product(xtlsFlows, [False, True]):
            addStream(addSecure(tcpStream(isObfs = False), xtlsFlow, udp443))  # TCP stream with XTLS
    for udpObfs in udpObfuscations:
        addStream(kcpStream(udpObfs))  # mKCP stream
        addStream(addSecure(kcpStream(udpObfs)))  # mKCP stream with TLS
        for xtlsFlow, udp443 in itertools.product(xtlsFlows, [False, True]):
            addStream(addSecure(kcpStream(udpObfs), xtlsFlow, udp443))  # mKCP stream with XTLS
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
