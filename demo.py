import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

# url = 'trojan://dnomd343@127.0.0.1:12345?security=tls&sni=local.343.re'
url = 'trojan://dnomd343@local.343.re:12345'

ret = Decoder.decode(url)
print(ret)
#
status, ret = Filter.filte(ret, isExtra = True)
print(status)
print(ret)

# info = {
#     'type': 'vmess',
#     'server': 'baidu.com',
#     'port': 12345,
#     'id': 'a859f794-1fcb-422e-bcad-3264dcea1f12',
#     'aid': 0,
#     'stream': {
#         'type': 'ws',
#         'host': 'host.343.re',
#         'secure': {
#             # 'sni': 'sni.343.re'
#         }
#     }
# }

# status, ret = Filter.filte(info, isExtra = True)
# print(status)
# print(ret)

data = Checker.proxyTest({
    'check': ['http'],
    'info': ret
})
print(data)
