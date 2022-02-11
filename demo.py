#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time

import ProxyBuilder as Builder
import ProxyChecker as Checker

workDir = '/tmp/ProxyC'

ssTest = {
    'tag': 'f43c9bae21ae8693',
    'check': [
        'http'
    ],
    'info': {
        'type': 'ss',
        'server': '127.0.0.1',
        'port': 12345,
        'password': 'dnomd343',
        'method': 'aes-256-ctr',
        'plugin': '',
        'pluginParam': '',
    }
}

ssrTest = {
    'tag': 'f43c9bae21ae8693',
    'check': [
        'http'
    ],
    'info': {
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
}

def loadDir(folderPath): # 创建文件夹
    try:
        if os.path.exists(folderPath): # 文件 / 文件夹 存在
            if not os.path.isdir(folderPath): # 文件
                return False # 无法创建
        else: # 不存在
            os.makedirs(folderPath) # 递归创建文件夹
        return True # 文件夹正常
    except:
        return False

def proxyTest(rawInfo, startDelay = 1, destroyDelay = 0.5):
    if loadDir(workDir) == False: # 工作文件夹无效
        return None
    if not 'info' in rawInfo:
        return None
    status, client = Builder.build(rawInfo['info'], workDir)
    if status != True:
        print(client)
        return None
    time.sleep(startDelay)
    if Builder.check(client) != True:
        print("client error")
        return None
    health, httpDelay = Checker.httpCheck(client['port'])
    print("health = " + str(health))
    if httpDelay < 0:
        print("http error")
    else:
        print("delay = " + format(httpDelay, '.2f') + 'ms')
    if Builder.destroy(client) != True:
        print("client destroy error")
    time.sleep(destroyDelay)
    print("done")

proxyTest(ssrTest)
