#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

vmessMethodList = [
    'aes-128-gcm',
    'chacha20-poly1305',
    'auto',
    'none',
    'zero',
]

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

vmessFilterRules = {
    'rootObject': {
        'remark': {
            'optional': True,
            'default': '',
            'type': str,
            'format': baseFunc.toStr
        },
        'server': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': baseFunc.isHost,
            'errMsg': 'Illegal server address'
        },
        'port': {
            'optional': True,
            'type': int,
            'format': baseFunc.toInt,
            'filter': baseFunc.isPort,
            'errMsg': 'Illegal port number'
        },
        'method': {
            'optional': False,
            'default': 'auto',
            'type': str,
            'format': lambda s: baseFunc.toStrTidy(s).replace('_', '-'),
            'filter': lambda method: method in vmessMethodList,
            'errMsg': 'Unknown VMess method'
        },
        'id': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
        },
        'aid': {
            'optional': False,
            'default': 0,
            'type': int,
            'format': baseFunc.toInt,
            # 'filter': 123,
            'filter': lambda aid: aid in range(0, 65536), # 0 ~ 65535
            'errMsg': 'Illegal alter Id'
        },
        'stream': {
            'optional': False,
            'default': {
                'type': 'tcp'
            },
            'type': [
                'tcpObject',
                'kcpObject',
                'wsObject',
                'h2Object',
                'quicObject',
                'grpcObject',
            ]
        }
    },
    'tcpObject': {
        'type': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'tcp',
            'errMsg': 'Unknown stream type'
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
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'kcp',
            'errMsg': 'Unknown stream type'
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
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'ws',
            'errMsg': 'Unknown stream type'
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
            'default': 2048,
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
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'h2',
            'errMsg': 'Unknown stream type'
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
            'default': None,
            'allowNone': True,
            'type': 'secureObject'
        }
    },
    'quicObject': {
        'type': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'quic',
            'errMsg': 'Unknown stream type'
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
            'format': baseFunc.toStrTidy,
            'filter': lambda streamType: streamType == 'grpc',
            'errMsg': 'Unknown stream type'
        },
        'service': {
            'optional': True,
            'type': str,
            'format': baseFunc.toStr
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
            'default': 'h2,http/1.1',
            'type': str,
            'format': baseFunc.toStr,
            'filter': lambda alpn: alpn in ['h2', 'http/1.1', 'h2,http/1.1'],
            'errMsg': 'Illegal alpn option'
        },
        'verify': {
            'optional': False,
            'default': True,
            'type': bool,
            'format': lambda b: b
        }
    }
}

def vmessFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    VMess节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'vmess',
                ...
            }
    """
    try:
        if not isExtra:
            vmessFilterRules['rootObject'].pop('remark')
        return baseFunc.ruleFilter(rawInfo, vmessFilterRules, {
            'type': 'vmess'
        })
    except:
        return False, 'Unknown error'
