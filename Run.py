#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import redis
import Check as Checker

redisPort = 6379
redisHost = 'localhost'
redisPrefix = 'proxyc-'

def __getCheckInfo() -> tuple[str or None, dict or None]:
    """
    获取检测任务

        无任务或发生异常:
            return None, None

        任务格式有误:
            return tag, None

        任务获取成功:
            return tag, {...}
    """
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
        tag = str(key[len(redisPrefix) + 8:], encoding = 'utf-8') # {prefix}check-x-{tag}
    except:
        return None, None
    try:
        return tag, json.loads(taskContent) # JSON解码
    except: # JSON解码失败
        return tag, None

def __setCheckResult(checkTag: str, checkResult: dict) -> bool: # 写入检测结果
    try:
        key = redisPrefix + 'result-' + checkTag
        redisObject.set(key, json.dumps(checkResult))
        return True
    except:
        return False

def main(startDelay: float, httpCheckUrl: str, httpCheckTimeout: int) -> None:
    checkTag, checkInfo = __getCheckInfo() # 获取检测任务
    if checkTag is None:
        print("no task found")
        return
    print(checkInfo)
    checkResult = Checker.proxyTest(
        checkInfo,
        startDelay = startDelay,
        httpCheckUrl = httpCheckUrl,
        httpCheckTimeout = httpCheckTimeout
    )
    if checkResult is None:
        print("some bad things happen")
        return
    elif not checkResult['success']:
        print("error proxy info")
        return
    print(checkTag + ' -> ', end = '')
    print(checkResult)
    if not __setCheckResult(checkTag, checkResult):
        print("redis write error")
        return

defaultStartDelay = 1.5
defaultHttpCheckTimeout = 20
defaultHttpCheckUrl = 'http://gstatic.com/generate_204'

redisObject = redis.StrictRedis(host = redisHost, port = redisPort, db = 0) # 连接Redis数据库

main(defaultStartDelay, defaultHttpCheckUrl, defaultHttpCheckTimeout)
