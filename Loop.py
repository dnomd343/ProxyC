#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import redis
import subprocess

maxThread = 32

redisPort = 6379
redisHost = 'localhost'
redisPrefix = 'proxyc-'

redisObject = redis.StrictRedis(
    db = 0,
    host = redisHost,
    port = redisPort
)

runScript = '/usr/local/share/ProxyC/Run.py'

processList = []
while True:
    spareNum = min(
        maxThread - len(processList), # 空余进程数
        len(redisObject.keys(redisPrefix + 'check-*')) # 待检测个数
    )
    if spareNum < 0: # 待运行进程数 > 0
        spareNum = 0
    for i in range(spareNum): # 运行检测进程
        processList.append(
            subprocess.Popen(['python', runScript])
        )
        time.sleep(0.2)

    for process in processList: # 遍历子进程
        if process.poll() != None: # 进程已退出
            processList.remove(process)

    time.sleep(0.5)
