import time

import ProxyBuilder as Builder
import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

# ret = Decoder.decode(url)
# print(ret)

info = {
    'type': 'hysteria',
    'server': '127.0.0.1',
    'port': 443,
    'protocol': 'faketcp',
    'obfs': 'dnomd343',
    'auth': 'dnomd343',
    'sni': 'local.343.re',
    'alpn': 'h3',
    'verify': False
}

status, ret = Filter.filte(info, isExtra = True)
print(status)
print(ret)
