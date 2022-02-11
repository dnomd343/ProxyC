#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import time
import subprocess

import test as Tester
import ProxyBuilder as Builder
import ProxyChecker as Checker

defaultPort = 10808
defaultPasswd = 'dnomd343'

def startTest(testList):
    for field in testList:
        serverProcess = subprocess.Popen(
            field['serverCommand'],
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL)
        time.sleep(0.1) # 等待进程启动
        if serverProcess.poll() != None: # 服务端启动失败
            print("server unexpected exit")
            continue
        print(field['caption'] + ' => ', end = '')
        status, client = Builder.build(field['proxyInfo'], '/tmp/ProxyC')
        time.sleep(0.5) # 等待初始化完成
        if Builder.check(client) != True:
            print("client unexpected exit") # 客户端启动失败
        else:
            status, delay = Checker.httpPing(client['port'])
            if status == True:
                print(format(delay, '.2f') + 'ms')
            else:
                print(delay)
            Builder.destroy(client) # 关闭客户端
            time.sleep(0.1)
        serverProcess.terminate() # 关闭服务端
        time.sleep(0.1)
        print()

if len(sys.argv) <= 1:
    print("no param")
    sys.exit(0)

testName = sys.argv[1]
if testName == 'ss':
    testList = Tester.Shadowsocks(defaultPort, defaultPasswd)
elif testName == 'ssr':
    testList = Tester.ShadowsocksR(defaultPort, defaultPasswd)
else:
    print("unknown test name")
    sys.exit(1)

startTest(testList)
