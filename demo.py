import ProxyDecoder as Decoder
import ProxyFilter as Filter

# info = {
#     'type': 'vless',
#     'server': '127.0.0.1',
#     'port': 12345,
#     'id': '1b1757d2-2ff1-4e8d-b62e-4e74c06f1325',
#     'stream': {
#         'type': 'grpc',
#         'service': 'dnomd343'
#     }
# }

# ret = Filter.filte(info)
# print(ret)

url = 'vmess://1b1757d2-2ff1-4e8d-b62e-4e74c06f1325@1.1.1.1:443'

ret = Decoder.decode(url)
print(ret)

status, ret = Filter.filte(ret, isExtra = True)
print(status)
print(ret)
