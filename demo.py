import time

import ProxyBuilder as Builder
import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

# url = 'brook://server?address=&insecure=&name=&password=password&server=1.2.3.4%3A9999&username='
# url = 'brook://server?address=&insecure=&name=&password=password&server=%5B2001%3A4860%3A4860%3A%3A8888%5D%3A9999&username='
# url = 'brook://wsserver?address=&insecure=&name=&password=password&username=&wsserver=ws%3A%2F%2F1.2.3.4%3A9999'
# url = 'brook://wsserver?address=&insecure=&name=&password=password&username=&wsserver=ws%3A%2F%2F%5B2001%3A4860%3A4860%3A%3A8888%5D%3A9999'
# url = 'brook://wssserver?address=1.2.3.4%3A443&insecure=true&name=&password=password&username=&wssserver=wss%3A%2F%2Fhello.com%3A443'
# url = 'brook://wsserver?address=1.2.3.4%3A443&name=&password=password&username=&wsserver=ws%3A%2F%2Fhello.com%3A443'

# url = 'ss://bf-cfb:test@192.168.100.1:8888#EXAMPLE'
# url = 'ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server'
url = 'ss://cmM0LW1kNTpwYXNzd2Q@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example'

ret = Decoder.decode(url)
print(ret)

status, ret = Filter.filte(ret, isExtra = True)
print(status)
print(ret)
