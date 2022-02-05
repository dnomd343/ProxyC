import time
import socket
import requests
import ProxyBuilder

def checkSocksPort(port):
    try:
        r = requests.get('http://gstatic.com/generate_204', proxies = {
            'http': 'socks5://127.0.0.1:' + str(port),
            'https': 'socks5://127.0.0.1:' + str(port),
        })
        if r.status_code == 204:
            return True
    except: pass
    return False

testInfo = {
    'type': 'shadowsocks',
    'server': '127.0.0.1',
    'port': 12345,
    'password': 'dnomd343',
    'method': 'aes-256-ctr',
    'plugin': '',
    'pluginArg': '',
}

print("start")
print(testInfo)
task = ProxyBuilder.build(testInfo, '/tmp/ProxyC')
print(task)
time.sleep(1)
if ProxyBuilder.check(task) == False:
    print("error exit")
else:
    print("test with gstatic")
    if checkSocksPort(task['port']):
        print("ok")
    else:
        print("error")
    ProxyBuilder.destroy(task)
    print("stop")
    