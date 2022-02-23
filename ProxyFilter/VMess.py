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
            'optional': False,
            'default': '',
            'type': str
        },
        'server': {
            'optional': True,
            'type': str,
            'format': lambda s: s.lower().strip(),
            'filter': baseFunc.isHost,
            'errMsg': 'Illegal server address'
        },
        'port': {
            'optional': True,
            'type': int,
            'format': lambda i: int(i),
            'filter': baseFunc.isPort,
            'errMsg': 'Illegal port number'
        },
        'method': {
            'optional': False,
            'default': 'auto',
            'type': str,
            'format': lambda s: s.replace('_', '-').lower().strip(),
            'filter': lambda method: method in vmessMethodList,
            'errMsg': 'Unknown VMess method'
        },
        'id': {
            'optional': True,
            'type': str
        },
        'aid': {
            'optional': False,
            'default': 0,
            'type': int,
            'format': lambda i: int(i),
            'filter': lambda aid: aid in range(0, 65536),
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
            'format': lambda s: s.lower().strip(),
            'filter': lambda streamType: streamType == 'tcp',
            'method': 'Unknown stream type'
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
            'format': lambda s: s.lower().strip(),
            'filter': lambda streamType: streamType == 'kcp',
            'method': 'Unknown stream type'
        },
        'seed': {
            'optional': False,
            'default': None,
            'allowNone': True,
            'type': str
        },
        'obfs': {
            'optional': False,
            'default': 'none',
            'type': str,
            'format': lambda s: s.replace('_', '-').lower().strip(),
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
            'format': lambda s: s.lower().strip(),
            'filter': lambda streamType: streamType == 'ws',
            'method': 'Unknown stream type'
        },
        'host': {
            'optional': False,
            'default': '',
            'type': str
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str
        },
        'ed': {
            'optional': False,
            'default': 2048,
            'format': lambda i: int(i),
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
            'format': lambda s: s.lower().strip(),
            'filter': lambda streamType: streamType == 'h2',
            'method': 'Unknown stream type'
        },
        'host': {
            'optional': False,
            'default': '',
            'type': str
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str
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
            'format': lambda s: s.lower().strip(),
            'filter': lambda streamType: streamType == 'quic',
            'method': 'Unknown stream type'
        },
        'method': {
            'optional': False,
            'default': 'none',
            'type': str,
            'format': lambda s: s.replace('_', '-').lower().strip(),
            'filter': lambda method: method in quicMethodList,
            'errMsg': 'Unknown QUIC method'
        },
        'passwd': {
            'optional': False,
            'default': '',
            'type': str
        },
        'obfs': {
            'optional': False,
            'default': 'none',
            'type': str,
            'format': lambda s: s.replace('_', '-').lower().strip(),
            'filter': lambda obfs: obfs in udpObfsList,
            'errMsg': 'Unknown QUIC obfs method'
        },
        'secure': {
            'optional': True,
            'type': 'secureObject'
        }
    },
    'grpcObject': {
        'type': {
            'optional': True,
            'type': str,
            'format': lambda s: s.lower().strip(),
            'filter': lambda streamType: streamType == 'grpc',
            'method': 'Unknown stream type'
        },
        'service': {
            'optional': True,
            'type': str
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
            'type': str
        },
        'path': {
            'optional': False,
            'default': '/',
            'type': str
        }
    },
    'secureObject': {
        'sni': {
            'optional': False,
            'default': '',
            'type': str
        },
        'alpn': {
            'optional': False,
            'default': 'h2,http/1.1',
            'type': str,
            'filter': lambda alpn: alpn in ['h2', 'http/1.1', 'h2,http/1.1'],
            'errMsg': 'Illegal alpn option'
        },
        'verify': {
            'optional': False,
            'default': True,
            'type': bool
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
        return baseFunc.rulesFilter(rawInfo, vmessFilterRules, {
            'type': 'vmess'
        })
    except:
        return False, 'Unknown error'
