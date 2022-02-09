import time
import socket
import requests

import ProxyBuilder as Builder
import ProxyChecker as Checker

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
print(dir(Checker))

print(testInfo)
task = Builder.build(testInfo, '/tmp/ProxyC')
print(task)
time.sleep(1)
if Builder.check(task) == False:
    print("error exit")
    Builder.destroy(task)
else:
    print("test with gstatic")
    health, delay = Checker.httpCheck(task['port'])
    print("health = " + str(health))
    if delay < 0:
        print("error")
    else:
        print("delay = " + format(delay, '.2f') + 'ms')
    Builder.destroy(task)
    print("stop")
