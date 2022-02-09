#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import subprocess

import test as Tester
import ProxyBuilder as Builder
import ProxyChecker as Checker

# print(dir(Tester))

# data = Tester.Shadowsocks(1081, 'dnomd343')
data = Tester.ShadowsocksR(1081, 'dnomd343')

# for field in data:
#     print(field['proxyInfo'])
#     print(field['serverCommand'])
#     print('')

for field in data:
    serverProcess = subprocess.Popen(
        field['serverCommand'],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL)
    time.sleep(0.1) # 等待进程启动
    if serverProcess.poll() != None: # 服务端启动失败
        print("server unexpected exit")
        continue
    print(field['caption'] + ' => ', end = '')
    client = Builder.build(field['proxyInfo'], '/tmp/ProxyC')
    time.sleep(0.5) # 等待初始化完成
    if not Builder.check(client):
        print("client unexpected exit") # 客户端启动失败
    else:
        print(format(Checker.httpPing(client['port']), '.2f') + 'ms')
        Builder.destroy(client) # 关闭客户端
        time.sleep(0.1)
    serverProcess.terminate() # 关闭服务端
    time.sleep(0.1)
    print()
