import time

import ProxyBuilder as Builder
import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

info = {
    'type': 'brook',
    'server': '127.0.0.1',
    'port': '12345',
    'passwd': 'dnomd343',
    # 'ws': {
    #     'host': 'local.343.re',
    #     'path': '/test',
    #     'secure': {
    #         'verify': False
    #     }
    # }
}

status, ret = Filter.filte(info)
print(status)
print(ret)

# print()
# status, ret = Builder.build(ret, '/tmp/ProxyC')
# print(status)
# print(ret)

data = Checker.proxyTest({
    'check': ['http'],
    'info': ret
})
print(data)
