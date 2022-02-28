#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import json

httpHeader = {
    'version': '1.1',
    'status': '200',
    'reason': 'OK',
    'headers': {
        'Content-Type': [
            'application/octet-stream',
            'video/mpeg'
        ],
        'Transfer-Encoding': [
            'chunked'
        ],
        'Connection': [
            'keep-alive'
        ],
        'Pragma': 'no-cache'
    }
}

kcpSetting = {
    'mtu': 1350,
    'tti': 20,
    'uplinkCapacity': 5,
    'downlinkCapacity': 20,
    'congestion': False,
    'readBufferSize': 1,
    'writeBufferSize': 1,
}

udpObfsList = [
    'none',
    'srtp',
    'utp',
    'wechat-video',
    'dtls',
    'wireguard'
]

quicMethodList = [
    'none',
    'aes-128-gcm',
    'chacha20-poly1305',
]

def loadTcpStream(isObfs: bool, host: str, path: str) -> dict:
    streamConfig = {
        'network': 'tcp',
        'tcpSettings': {
            'type': 'none'
        }
    }
    if not isObfs: # 不带http混淆
        return {
            'caption': 'TCP',
            'client': {
                'type': 'tcp',
                'secure': None
            },
            'server': streamConfig
        }

    streamConfig['tcpSettings'] = { # http混淆配置
        'header': {
            'type': 'http',
            'response': httpHeader
        }
    }
    return {
        'caption': 'TCP with http obfs',
        'client': {
            'type': 'tcp',
            'obfs': {
                'host': host,
                'path': path
            },
            'secure': None
        },
        'server': streamConfig
    }

def loadKcpStream(seed: str, obfs: str) -> dict:
    kcpSetting['header'] = {
        'type': obfs
    }
    kcpSetting['seed'] = seed
    return {
        'caption': 'mKCP obfs ' + obfs,
        'client': {
            'type': 'kcp',
            'seed': seed,
            'obfs': obfs,
            'secure': None
        },
        'server': {
            'network': 'kcp',
            'kcpSettings': kcpSetting
        }
    }

def loadWsStream(host: str, path: str, isEd: bool) -> dict:
    wsSetting = {
        'path': path,
        'headers': {
            'Host': host
        }
    }
    if not isEd: # 不带Early Data
        return {
            'caption': 'WebSocket',
            'client': {
                'type': 'ws',
                'host': host,
                'path': path,
                'secure': None
            },
            'server': {
                'network': 'ws',
                'wsSettings': wsSetting
            }
        }
    wsSetting['maxEarlyData'] = 2048
    wsSetting['earlyDataHeaderName'] = 'Sec-WebSocket-Protocol'
    return {
        'caption': 'WebSocket Max-Early-Data 2048',
        'client': {
            'type': 'ws',
            'host': host,
            'path': path,
            'ed': 2048,
            'secure': None
        },
        'server': {
            'network': 'ws',
            'wsSettings': wsSetting
        }
    }

def loadH2Stream(host: str, path: str) -> dict:
    return {
        'caption': 'HTTP/2',
        'client': {
            'type': 'h2',
            'host': host,
            'path': path,
            'secure': None
        },
        'server': {
            'network': 'http',
            'httpSettings': {
                'host': [host],
                'path': path
            }
        }
    }

def loadQuicStream(method: str, passwd: str, obfs: str) -> dict:
    return {
        'caption': 'QUIC method ' + method + ' obfs ' + obfs,
        'client': {
            'type': 'quic',
            'method': method,
            'passwd': passwd,
            'obfs': obfs,
            'secure': None
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

def loadGrpcStream(service: str, multiMode: bool = False) -> dict:
    if not multiMode:
        return {
            'caption': 'gRPC',
            'client': {
                'type': 'grpc',
                'service': service,
                'secure': None
            },
            'server': {
                'network': 'grpc',
                'grpcSettings': {
                    'serviceName': service
                }
            }
        }
    return {
        'caption': 'gRPC multi-mode',
        'client': {
            'type': 'grpc',
            'service': service,
            'mode': 'multi',
            'secure': None
        },
        'server': {
            'network': 'grpc',
            'grpcSettings': {
                'serviceName': service,
                'multiMode': True # gRPC multi-mode not work in v2fly-core
            }
        }
    }

def addSecureConfig(rawStreamInfo: dict, cert: str, key: str, sni: str) -> dict:
    streamInfo = copy.deepcopy(rawStreamInfo)
    streamInfo['caption'] += ' (tls)'
    streamInfo['client']['secure'] = {
        'sni': sni
    }
    streamInfo['server']['security'] = 'tls'
    streamInfo['server']['tlsSettings'] = {
        'alpn': [
            'h2',
            'http/1.1'
        ],
        'certificates': [
            {
                'certificateFile': cert,
                'keyFile': key
            }
        ]
    }
    return streamInfo

def v2rayConfig(inboundConfig: dict) -> str:
    return json.dumps({
        'log': {
            'loglevel': 'warning'
        },
        'inbounds': [inboundConfig],
        'outbounds': [
            {
                'protocol': 'freedom'
            }
        ]
    })
