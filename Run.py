#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import redis
import Checker

def __loadRedis(redisHost = 'localhost', redisPort = 6379): # 连接Redis数据库
    return redis.StrictRedis(host = redisHost, port = redisPort, db = 0)

def __getCheckInfo(redisObject, redisPrefix):
    '''
    获取检测任务

        无任务或发生异常:
            return None, None

        任务格式有误:
            return tag, None

        任务获取成功:
            return tag, {...}
    '''
    try:
        checkList = redisObject.keys(redisPrefix + 'check-a-*') # 优先级排序
        if len(checkList) == 0:
            checkList = redisObject.keys(redisPrefix + 'check-b-*')
        if len(checkList) == 0:
            checkList = redisObject.keys(redisPrefix + 'check-c-*')
        if len(checkList) == 0:
            checkList = redisObject.keys(redisPrefix + 'check-d-*')
        if len(checkList) == 0:
            checkList = redisObject.keys(redisPrefix + 'check-e-*')
        if len(checkList) == 0: # 无任务
            return None, None
        key = checkList[0] # 选取首个任务
        taskContent = redisObject.get(key) # 获取任务信息
        redisObject.delete(key) # 删除任务记录
        tag = str(key[len(redisPrefix) + 8:], encoding = "utf-8") # {prefix}check-x-{tag}
    except:
        return None, None
    try:
        return tag, json.loads(taskContent) # JSON解码
    except: # JSON解码失败
        return tag, None

def __setCheckResult(checkTag, checkResult, redisObject, redisPrefix): # 写入检测结果
    try:
        key = redisPrefix + 'result-' + checkTag
        redisObject.set(key, json.dumps(checkResult))
        return True
    except:
        return False

def main(startDelay, httpCheckUrl, httpCheckTimeout):
    redisPrefix = 'proxyc-'
    redisObject = __loadRedis()
    checkTag, checkInfo = __getCheckInfo(redisObject, redisPrefix) # 获取检测任务
    if checkTag == None:
        print("no task found")
        return
    print(checkInfo)
    checkResult = Checker.proxyTest(
        checkInfo,
        startDelay = startDelay,
        httpCheckUrl = httpCheckUrl,
        httpCheckTimeout = httpCheckTimeout
    )
    if checkResult == None:
        print("some bad things happen")
        return
    elif checkResult['success'] == False:
        print("error proxy info")
        return
    print(checkResult)
    if __setCheckResult(checkTag, checkResult, redisObject, redisPrefix) == False:
        print("redis write error")
        return
    print("ok")

defaultStartDelay = 1.5
defaultHttpCheckTimeout = 20
defaultHttpCheckUrl = 'http://gstatic.com/generate_204'

main(defaultStartDelay, defaultHttpCheckUrl, defaultHttpCheckTimeout)
