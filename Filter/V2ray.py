#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis.Filter import rulesFilter
from Basis.Constant import quicMethods, udpObfuscations
from Basis.Functions import toInt, toStr, toStrTidy, toBool

tlsObject = rulesFilter({
    'sni': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid SNI content'
    },
    'alpn': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': lambda s: toStrTidy(s).replace(' ', ''),  # remove space
        'filter': lambda s: s in ['h2', 'http/1.1', 'h2,http/1.1'],
        'errMsg': 'Invalid alpn option'
    },
    'verify': {
        'optional': True,
        'default': True,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid verify option'
    }
})

obfsObject = rulesFilter({
    'host': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid obfs host'
    },
    'path': {
        'optional': True,
        'default': '/',
        'type': str,
        'format': lambda s: toStr(s).strip(),
        'errMsg': 'Invalid obfs path'
    }
})

tcpObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'tcp',
        'errMsg': 'Invalid TCP stream type'
    },
    'obfs': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': obfsObject,
        'errMsg': 'Invalid obfsObject'
    },
    'secure': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': tlsObject,
        'errMsg': 'Invalid tlsObject'
    }
})

kcpObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'kcp',
        'errMsg': 'Invalid mKCP stream type'
    },
    'seed': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid mKCP seed'
    },
    'obfs': {
        'optional': True,
        'default': 'none',
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in udpObfuscations,
        'errMsg': 'Unknown mKCP obfs method'
    },
    'secure': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': tlsObject,
        'errMsg': 'Invalid tlsObject'
    }
})

wsObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'ws',
        'errMsg': 'Invalid WebSocket stream type'
    },
    'host': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid WebSocket host'
    },
    'path': {
        'optional': True,
        'default': '/',
        'type': str,
        'format': lambda s: toStr(s).strip(),
        'errMsg': 'Invalid WebSocket path'
    },
    'ed': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': int,
        'format': toInt,
        'filter': lambda i: i > 0,
        'errMsg': 'Illegal Max-Early-Data length'
    },
    'secure': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': tlsObject,
        'errMsg': 'Invalid tlsObject'
    }
})

h2Object = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'h2',
        'errMsg': 'Invalid HTTP/2 stream type'
    },
    'host': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid HTTP/2 host'
    },
    'path': {
        'optional': True,
        'default': '/',
        'type': str,
        'format': lambda s: toStr(s).strip(),
        'errMsg': 'Invalid HTTP/2 path'
    },
    'secure': {
        'optional': True,
        'default': {},
        'type': tlsObject,
        'errMsg': 'Invalid tlsObject'
    }
})

quicObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'quic',
        'errMsg': 'Invalid QUIC stream type'
    },
    'method': {
        'optional': True,
        'default': 'none',
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in quicMethods,
        'errMsg': 'Unknown QUIC method'
    },
    'passwd': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid QUIC password'
    },
    'obfs': {
        'optional': True,
        'default': 'none',
        'type': str,
        'format': lambda s: toStrTidy(s).replace('_', '-'),
        'filter': lambda s: s in udpObfuscations,
        'errMsg': 'Unknown QUIC obfs method'
    },
    'secure': {
        'optional': True,
        'default': {},
        'type': tlsObject,
        'errMsg': 'Invalid tlsObject'
    }
})

grpcObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'grpc',
        'errMsg': 'Invalid gRPC stream type'
    },
    'service': {
        'type': str,
        'format': lambda s: toStr(s).strip(),
        'errMsg': 'Invalid service content'
    },
    'mode': {
        'optional': True,
        'default': 'gun',
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s in ['gun', 'multi'],
        'errMsg': 'Unknown gRPC mode'
    },
    'secure': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': tlsObject,
        'errMsg': 'Invalid tlsObject'
    }
})
