import time

import ProxyBuilder as Builder
import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

# info = {
#     'type': 'trojan-go',
#     'server': '127.0.0.1',
#     'port': 12345,
#     'passwd': 'dnomd343',
#     'sni': 'local.343.re',
#     'plugin': {
#         'type': 'simple-tls',
#         'param': 'n=local.343.re;no-verify'
#     }
# }
#
# status, ret = Filter.filte(info, isExtra = True)
# print(status)
# print(ret)
#
# data = Checker.proxyTest({
#     'check': ['http'],
#     'info': ret
# })
#
# print(data)

url = 'trojan-go://password1234@google.com/?sni=microsoft.com&type=ws&host=youtube.com&path=%2Fgo&encryption=ss%3Baes-256-gcm%3Afuckgfw&plugin=obfs-local%3Bobfs%3Dhttp%3Bobfs-host%3Dwww.bing.com#server%20name'
ret = Decoder.decode(url)
print(ret)

ret = Filter.filte(ret)
print(ret)
