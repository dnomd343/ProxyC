import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

info = {
    'type': 'trojan-go',
    'server': '127.0.0.1',
    'port': '12345',
    'passwd': 'dnomd343',
    'sni': 'local.343.re',
    'alpn': 'h2',
    'verify': False,
    'ws': {
        'host': 'local.343.re',
        'path': '/test'
    },
    'ss': {
        'method': 'chacha20-ietf-poly1305',
        'passwd': 'dnomd343'
    },
    'plugin': {
        'type': 'obfs-local',
        'param': 'obfs=http'
    }
}

status, ret = Filter.filte(info, isExtra = True)
print(status)
print(ret)
