#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

httpConfig = {
    'type': 'http',
    'request': {
        'version': '1.1',
        'method': 'GET',
        'path': [],
        'headers': {
            'Host': [],
            'User-Agent': [
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 '
                '(KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46',
            ],
            'Accept-Encoding': ['gzip, deflate'],
            'Connection': ['keep-alive'],
            'Pragma': 'no-cache',
        }
    }
}

kcpConfig = {
    'mtu': 1350,
    'tti': 50,
    'uplinkCapacity': 12,
    'downlinkCapacity': 100,
    'congestion': False,
    'readBufferSize': 2,
    'writeBufferSize': 2,
    'header': {}
}


def loadSecure(secureInfo: dict or None) -> dict:  # TLS encrypt config
    if secureInfo is None:
        return {'security': 'none'}  # without TLS options
    tlsObject = {
        'allowInsecure': not secureInfo['verify']  # whether verify server's certificate
    }
    if secureInfo['alpn'] is not None:
        tlsObject['alpn'] = secureInfo['alpn'].split(',')  # multi-alpn like `h2,http/1.1`
    if secureInfo['sni'] != '':
        tlsObject['serverName'] = secureInfo['sni']  # SNI field in TLS protocol
    return {
        'security': 'tls',
        'tlsSettings': tlsObject
    }


def tcpStream(streamInfo: dict) -> dict:  # TCP stream config
    tcpObject = {}
    if streamInfo['obfs'] is not None:  # enable http obfs options
        httpObject = copy.deepcopy(httpConfig)
        httpObject['request']['path'].append(streamInfo['obfs']['path'])  # obfs path (start with '/')
        httpObject['request']['headers']['Host'] = streamInfo['obfs']['host'].split(',')  # obfs host (maybe multiple)
        tcpObject['header'] = httpObject
    return {
        'network': 'tcp',
        'tcpSettings': tcpObject
    }


def kcpStream(streamInfo: dict) -> dict:  # mKCP stream config
    kcpObject = copy.deepcopy(kcpConfig)
    kcpObject['header']['type'] = streamInfo['obfs']  # mKCP header type -> none / srtp / utp / ...
    if streamInfo['seed'] is not None:
        kcpObject['seed'] = streamInfo['seed']  # mKCP obfs password
    return {
        'network': 'kcp',
        'kcpSettings': kcpObject
    }


def wsStream(streamInfo: dict) -> dict:  # WebSocket stream config
    wsObject = {
        'path': streamInfo['path']  # websocket connection path
    }
    if streamInfo['host'] != '':  # empty host should not be set
        wsObject['headers'] = {}
        wsObject['headers']['Host'] = streamInfo['host']
    if streamInfo['ed'] is not None:  # with early data options
        wsObject['maxEarlyData'] = streamInfo['ed']
        wsObject['earlyDataHeaderName'] = 'Sec-WebSocket-Protocol'
    return {
        'network': 'ws',
        'wsSettings': wsObject
    }


def h2Stream(streamInfo: dict) -> dict:  # HTTP/2 stream config
    h2Object = {
        'path': streamInfo['path']  # http/2 connection path
    }
    if streamInfo['host'] != '':  # empty host should not be set
        h2Object['host'] = streamInfo['host'].split(',')  # http/2 host maybe multiple
    return {
        'network': 'http',
        'httpSettings': h2Object
    }


def quicStream(streamInfo: dict) -> dict:  # QUIC stream config
    return {
        'network': 'quic',
        'quicSettings': {
            'security': streamInfo['method'],
            'key': streamInfo['passwd'],
            'header': {
                'type': streamInfo['obfs']
            }
        }
    }


def grpcStream(streamInfo: dict) -> dict:  # gRPC stream config
    grpcObject = {
        'serviceName': streamInfo['service']  # gRPC service name
    }
    if streamInfo['mode'] == 'multi':  # gRPC multi-mode not work in v2fly-core
        grpcObject['multiMode'] = True
    return {
        'network': 'grpc',
        'grpcSettings': grpcObject
    }


def loadStream(streamInfo: dict) -> dict:
    streamEntry = {
        'tcp': tcpStream,
        'kcp': kcpStream,
        'ws': wsStream,
        'h2': h2Stream,
        'quic': quicStream,
        'grpc': grpcStream,
    }
    if streamInfo['type'] not in streamEntry:
        raise RuntimeError('Unknown stream type')
    streamObject = streamEntry[streamInfo['type']](streamInfo)
    return {
        **streamObject,
        **loadSecure(streamInfo['secure'])
    }


def loadConfig(socksInfo: dict, outboundObject: dict) -> dict:  # load config by socks and outbound info
    return {
        'log': {
            'loglevel': 'debug'
        },
        'inbounds': [{  # expose socks5 interface (inbound)
            'port': socksInfo['port'],
            'listen': socksInfo['addr'],
            'protocol': 'socks',
            'settings': {
                'udp': True,
                'auth': 'noauth'
            }
        }],
        'outbounds': [outboundObject]  # outbound without route object
    }
