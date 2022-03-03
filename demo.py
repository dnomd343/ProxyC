import time

import ProxyBuilder as Builder
import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

# info = {
#     'type': 'brook',
#     'server': '127.0.0.1',
#     'port': '12345',
#     'passwd': 'dnomd343',
#     # 'ws': {
#     #     'host': 'local.343.re',
#     #     'path': '/test',
#     #     'secure': {
#     #         'verify': False
#     #     }
#     # }
# }
#
# status, ret = Filter.filte(info)
# print(status)
# print(ret)
#
# # print()
# # status, ret = Builder.build(ret, '/tmp/ProxyC')
# # print(status)
# # print(ret)
#
# data = Checker.proxyTest({
#     'check': ['http'],
#     'info': ret
# })
# print(data)


url = 'brook://server?address=&insecure=&name=&password=password&server=1.2.3.4%3A9999&username='
url = 'brook://server?address=&insecure=&name=&password=password&server=%5B2001%3A4860%3A4860%3A%3A8888%5D%3A9999&username='
url = 'brook://wsserver?address=&insecure=&name=&password=password&username=&wsserver=ws%3A%2F%2F1.2.3.4%3A9999'
url = 'brook://wsserver?address=&insecure=&name=&password=password&username=&wsserver=ws%3A%2F%2F%5B2001%3A4860%3A4860%3A%3A8888%5D%3A9999'
url = 'brook://wssserver?address=1.2.3.4%3A443&insecure=true&name=&password=password&username=&wssserver=wss%3A%2F%2Fhello.com%3A443'
url = 'brook://wsserver?address=1.2.3.4%3A443&name=&password=password&username=&wsserver=ws%3A%2F%2Fhello.com%3A443'

ret = Decoder.decode(url)
print(ret)

status, ret = Filter.filte(ret, isExtra = True)
print(status)
print(ret)
