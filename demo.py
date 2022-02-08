import time
import socket
import requests
import ProxyBuilder as Builder

def checkSocksPort(port):
    try:
        startTime = time.time_ns()
        r = requests.get('http://gstatic.com/generate_204', proxies = {
            'http': 'socks5://127.0.0.1:' + str(port),
            'https': 'socks5://127.0.0.1:' + str(port),
        })
        if r.status_code == 204:
            delay = (time.time_ns() - startTime) / (10 ** 6)
            print(format(delay, '.2f') + 'ms')
            return True
    except: pass
    return False

# testInfo = {
#     'type': 'ss',
#     'server': '127.0.0.1',
#     'port': 12345,
#     'password': 'dnomd343',
#     'method': 'aes-256-ctr',
#     'plugin': '',
#     'pluginArg': '',
# }

testInfo = {
    'type': 'ssr',
    "server": "127.0.0.1",
    "port": 23456,
    "password": "dnomd343",
    "method": "table",
    "protocol": "auth_aes128_md5",
    "protocolParam": "",
    "obfs": "tls1.2_ticket_auth",
    "obfsParam": ""
}

print("start")

print(dir(Builder))

print(testInfo)
task = Builder.build(testInfo, '/tmp/ProxyC')
print(task)
time.sleep(1)
if Builder.check(task) == False:
    print("error exit")
else:
    print("test with gstatic")
    checkSocksPort(task['port'])
    checkSocksPort(task['port'])
    checkSocksPort(task['port'])
    if checkSocksPort(task['port']):
        print("ok")
    else:
        print("error")
    Builder.destroy(task)
    print("stop")
