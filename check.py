#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import json
import redis

import ProxyBuilder as Builder
import ProxyChecker as Checker

workDir = '/tmp/ProxyC'
redisPrefix = 'proxyc-'
redisHost = 'localhost'
redisPort = 6379

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

def proxyHttpCheck(socksPort): # Http检测
    try:
        health, httpDelay = Checker.httpCheck(socksPort, timeout = 12)
        if health == None: # 连接失败
            return None
        return {
            'delay': httpDelay,
            'health': health
        }
    except: # 未知错误
        return None

def proxyTest(rawInfo, startDelay = 1):
    '''
    代理检测入口

        异常错误:
            return None

        启动失败:
            return {
                'success': False
            }

        测试完成:
            return {
                'success': True,
                'result': checkResult
            }

    '''
    if loadDir(workDir) == False: # 工作文件夹无效
        return None
    if not 'info' in rawInfo: # 缺少代理服务器信息
        return None

    try:
        status, client = Builder.build(rawInfo['info'], workDir)
    except: # 构建发生未知错误
        Builder.destroy(client)
        return None
    if status == None: # 构建错误
        Builder.destroy(client)
        return None
    elif status == False: # 节点信息有误
        return {
            'success': False
        }

    time.sleep(startDelay) # 延迟等待客户端启动
    status = Builder.check(client) # 检查客户端状态
    if status == None: # 检测失败
        Builder.destroy(client)
        return None
    elif status == False: # 客户端异常退出
        Builder.destroy(client)
        return {
            'success': False
        }

    if not 'check' in rawInfo: # 缺少检测项目
        return None
    checkItem = rawInfo['check']
    checkResult = {}
    for item in checkItem:
        if item == 'http': # http检测
            result = proxyHttpCheck(client['port'])
        else: # 未知检测项目
            result = None
        if result == None: # 检测出错
            Builder.destroy(client)
            return None
        checkResult[item] = result

    Builder.destroy(client) # 销毁客户端
    return {
        'success': True,
        'result': checkResult
    }

def getTask(): # 获取检测任务
    redisObject = redis.StrictRedis(host = redisHost, port = redisPort, db = 0)
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
        return None
    key = checkList[0] # 选取首个任务
    taskContent = redisObject.get(key)
    redisObject.delete(key)
    tag = str(key[len(redisPrefix) + 8:], encoding = "utf-8")
    try:
        return tag, json.loads(taskContent) # JSON解码
    except: # JSON解码失败
        return tag, None

def setResult(tag, result): # 写入检测结果
    redisObject = redis.StrictRedis(host = redisHost, port = redisPort, db = 0)
    key = redisPrefix + 'result-' + tag
    redisObject.set(key, json.dumps(result))

def main():
    try:
        taskTag, task = getTask() # 获取检测任务
    except:
        return
    if task == None:
        return
    try:
        setResult(taskTag, proxyTest(task)) # 检测并写入数据库
    except:
        pass

main()
