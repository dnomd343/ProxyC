#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

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

v2rayStreamRules = {
    'tcpObject': {
        'type': {
            'optional': True,
            'type': str,
            'indexKey': True,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'tcp',
            'errMsg': 'Unexpected stream type'
        },
        'obfs': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'obfsObject'
        },
        'secure': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'secureObject'
        }
    },
    'kcpObject': {
        'type': {
            'optional': True,
            'type': str,
            'indexKey': True,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'kcp',
            'errMsg': 'Unexpected stream type'
        },
        'seed': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'obfs': {
            'optional': False,
            'default': 'none',
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
            'filter': lambda obfs: obfs in udpObfsList,
            'errMsg': 'Unknown mKCP obfs method'
        },
        'secure': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'secureObject'
        }
    },
    'wsObject': {
        'type': {
            'optional': True,
            'type': str,
            'indexKey': True,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'ws',
            'errMsg': 'Unexpected stream type'
        },
        'host': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str,
            'format': baseFunc.toStr
        },
        'ed': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': int,
            'format': baseFunc.toInt,
            'filter': lambda ed: ed > 0,
            'errMsg': 'Illegal Max-Early-Data length'
        },
        'secure': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'secureObject'
        }
    },
    'h2Object': {
        'type': {
            'optional': True,
            'type': str,
            'indexKey': True,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'h2',
            'errMsg': 'Unexpected stream type'
        },
        'host': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str,
            'format': baseFunc.toStr
        },
        'secure': {
            'optional': False,
            'default': {},
            'type': 'secureObject'
        }
    },
    'quicObject': {
        'type': {
            'optional': True,
            'type': str,
            'indexKey': True,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'quic',
            'errMsg': 'Unexpected stream type'
        },
        'method': {
            'optional': False,
            'default': 'none',
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
            'filter': lambda method: method in quicMethodList,
            'errMsg': 'Unknown QUIC method'
        },
        'passwd': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'obfs': {
            'optional': False,
            'default': 'none',
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
            'filter': lambda obfs: obfs in udpObfsList,
            'errMsg': 'Unknown QUIC obfs method'
        },
        'secure': {
            'optional': False,
            'default': {},
            'type': 'secureObject'
        }
    },
    'grpcObject': {
        'type': {
            'optional': True,
            'type': str,
            'indexKey': True,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'grpc',
            'errMsg': 'Unexpected stream type'
        },
        'service': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'mode': {
            'optional': False,
            'default': 'gun',
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': lambda mode: mode in ['gun', 'multi'],
            'errMsg': 'Unknown gRPC mode'
        },
        'secure': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': 'secureObject'
        }
    },
    'obfsObject': {
        'host': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str,
            'format': baseFunc.toStr
        }
    },
    'secureObject': {
        'sni': {
            'optional': False,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'alpn': {
            'optional': False,
            'default': None,
            'allowNone': True,
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
}
