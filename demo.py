import ProxyDecoder as Decoder
import ProxyFilter as Filter

url = 'vless://...'

ret = Decoder.decode(url)
print(ret)

status, ret = Filter.filte(ret, isExtra = True)
print(status)
print(ret)
