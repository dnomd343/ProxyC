#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import redis
import random
import hashlib
from flask import Flask, request

apiPath = '/'
api = Flask(__name__)

redisPort = 6379
redisHost = 'localhost'
redisPrefix = 'proxyc-'

accessToken = 'dnomd343'

def httpPostArg(field: str): # 获取HTTP POST参数
    try:
        if request.values.get(field) != None: # application/x-www-form-urlencoded
            return request.values.get(field)
        elif request.json.get(field) != None: # application/json
            return request.json.get(field)
        elif request.form.get(field) != None: # multipart/form-data
            return request.form.get(field)
    except:
        pass
    return None

def genRandomId(length = 24): # 生成随机ID
    tag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            tag += chr(tmp + 87) # a ~ f
        else:
            tag += str(tmp) # 0 ~ 9
    return tag

def genError(message: str): # 生成JSON错误回复
    return {
        'success': False,
        'message': message
    }

def getAllTask(): # 获取当前所有检测任务
    # TODO: redis query
    # print(redisObject.keys(redisPrefix + '*'))
    return [
        '54cd9ba3a8e86f93',
        'f43c9bae21ae8693',
    ]

def addCheckTask(priority, checkList, proxyList): # 检测任务加入数据库
    digestList = []
    checkId = genRandomId()
    for proxyInfo in proxyList:
        digest = hashlib.md5(json.dumps({
            'check': checkList,
            'info': proxyInfo,
        }).encode(encoding = 'UTF-8')).hexdigest() # 计算节点摘要
        digestList.append(digest)
        repeatKey = redisObject.keys(redisPrefix + 'check-*-' + digest)
        if repeatKey != []: # 存在重复
            repeatKey = str(repeatKey[0], encoding = 'utf-8')
            repeatPriority = repeatKey[len(redisPrefix) + 6:][:1] # 获取原优先级
            if ord(repeatPriority) > ord(priority): # 原优先级较低
                redisObject.rename( # 提升优先级
                    repeatKey,
                    redisPrefix + 'check-' + priority + '-' + digest
                )
        else:
            redisObject.set( # 写入数据库
                redisPrefix + 'check-' + priority + '-' + digest,
                json.dumps({
                    'tag': digest,
                    'check': checkList,
                    'info': proxyInfo
                })
            )
    redisObject.set( # 记录任务
        redisPrefix + 'task-' + checkId,
        json.dumps({
            'checkId': checkId,
            'priority': priority,
            'check': checkList,
            'proxy': digestList,
            'checkNum': len(digestList),
            'completeNum': 0
        })
    )

def getCheckList(): # 获取检测任务列表
    if request.args.get('token') != accessToken: # token无效
        return genError('invalid token')
    return {
        'success': True,
        'taskList': getAllTask()
    }

def newCheckTask(): # 新增检测任务
    import ProxyDecoder as Decoder
    import ProxyFilter as Filter

    if httpPostArg('token') != accessToken: # token无效
        return genError('invalid token')

    priority = httpPostArg('priority') # 优先级选项
    if not priority in ['a','b','c','d','e']:
        priority = 'c' # 默认优先级

    checkList = httpPostArg('check') # 检测列表
    if checkList == None:
        return genError('missing check list')
    for checkMethod in checkList:
        if not checkMethod in ['http']:
            return genError('unknown check method `' + checkMethod + '`')

    proxyList = httpPostArg('proxy') # 代理列表
    if proxyList == None:
        return genError('missing proxy list')
    if isinstance(proxyList, str): # 单项任务
        proxyList = [ proxyList ]
    for i in range(0, len(proxyList)):
        if isinstance(proxyList[i], str): # 解码分享链接
            proxyList[i] = Decoder.decode(proxyList[i])
            if proxyList[i] == None:
                return genError('could not decode index ' + str(i))
        status, proxyList[i] = Filter.filter(proxyList[i]) # 节点信息检查
        if status == False: # 节点不合法
            return genError('index ' + str(i) + ': ' + proxyList[i])

    checkId = addCheckTask(priority, checkList, proxyList) # 任务加入数据库
    if checkId == None: # 异常错误
        return genError('server error')
    return {
        'success': True,
        'checkId': checkId
    }

def getTaskInfo(checkId): # 获取任务详情
    # TODO: get task info from redis
    return {
        'success': True,
        'checkId': checkId
    }

def deleteTask(checkId): # 删除任务
    # TODO: delete task from redis
    return {
        'success': True,
        'checkId': checkId
    }

@api.route(apiPath + '/check', methods = ['GET','POST'])
def apiCheck():
    if request.method == 'GET':
        return getCheckList()
    elif request.method == 'POST':
        return newCheckTask()

@api.route(apiPath + '/check/<checkId>', methods = ['GET','DELETE'])
def check_id(checkId):
    if request.method == 'GET':
        return getTaskInfo(checkId)
    elif request.method == 'POST':
        return deleteTask(checkId)

redisObject = redis.StrictRedis(
    db = 0,
    host = redisHost,
    port = redisPort
)
api.run(host = '0.0.0.0', port = 43581, debug = True)
