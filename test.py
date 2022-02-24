#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import subprocess
import Checker
import ProxyTester as Tester

def testBuild(config: dict):
    if config['filePath'] is not None:
        with open(config['filePath'], 'w') as fileObject:  # 保存文件
            fileObject.write(config['fileContent'])
    return subprocess.Popen( # 进程启动
        config['startCommand'],
        env = config['envVar'],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL
    )

def testDestroy(config: dict, process):
    if process.poll() is None:  # 未死亡
        while process.poll() is None:  # 等待退出
            process.terminate()  # SIGTERM
            time.sleep(0.2)
    if config['filePath'] is not None:
        os.remove(config['filePath']) # 删除文件

testList = Tester.test('ss')

aiderProcess = None
serverProcess = None
for testMethod in testList:
    # print()
    # print()
    # print(testMethod)
    # continue
    print(testMethod['caption'], end = ' -> ')

    serverProcess = testBuild(testMethod['server'])
    if testMethod['aider'] is not None:
        aiderProcess = testBuild(testMethod['aider'])

    ret = Checker.proxyTest({
        'check': ['http'],
        'info': testMethod['proxy']
    })
    if not ret['success']:
        print('check error')
    delay = ret['check']['http']['delay']
    print(str(delay) + 'ms')

    testDestroy(testMethod['server'], serverProcess)
    if testMethod['aider'] is not None:
        testDestroy(testMethod['aider'], aiderProcess)

# testName = sys.argv[1]
# if testName == 'ss':
#     testList = Tester.Shadowsocks(defaultPort, defaultPasswd)
# elif testName == 'ssr':
#     testList = Tester.ShadowsocksR(defaultPort, defaultPasswd)
# else:
#     print("unknown test name")
#     sys.exit(1)
#
# startTest(testList)
