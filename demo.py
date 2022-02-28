import ProxyDecoder as Decoder
import ProxyFilter as Filter

url = 'trojan://dnomd343@1.1.1.1:443?security=tls&type=tcp&headerType=http&host=ip.343.re'

ret = Decoder.decode(url)
print(ret)

status, ret = Filter.filte(ret, isExtra = True)
print(status)
print(ret)
