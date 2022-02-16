#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import redis
import random
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

def addCheckTask(priority, checkList, proxyList): # 检测任务加入数据库
    try:
        tagList = []
        for proxyInfo in proxyList:
            tag = genRandomId(32) # 32位检测ID
            tagList.append(tag)
            redisObject.set( # 写入数据库
                redisPrefix + 'check-' + priority + '-' + tag,
                json.dumps({
                    'tag': tag,
                    'check': checkList,
                    'info': proxyInfo
                })
            )
        checkId = genRandomId(24) # 24位任务ID
        redisObject.set( # 记录任务
            redisPrefix + 'task-' + checkId,
            json.dumps({
                'checkId': checkId,
                'priority': priority,
                'check': checkList,
                'proxy': tagList,
                'complete': False
            })
        )
        return checkId
    except: # 异常错误
        return None

def getCheckList(): # 获取检测任务列表
    try:
        if request.args.get('token') != accessToken: # token无效
            return genError('invalid token')
        taskList = []
        rawTaskList = redisObject.keys(redisPrefix + 'task-*')
        for task in rawTaskList: # 获取任务ID
            taskList.append(str(task[len(redisPrefix) + 5:], encoding = 'utf-8'))
        return {
            'success': True,
            'taskList': taskList
        }
    except:
        return genError('server error')

def newCheckTask(): # 新增检测任务
    try:
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
    except:
        return genError('server error')

def getTaskInfo(checkId): # 获取任务详情
    try:
        taskKey = redisObject.keys(redisPrefix + 'task-' + checkId)
        if taskKey == []: # 任务ID不存在
            return genError('invalid check id')
        taskKey = str(taskKey[0], encoding = 'utf-8')
        taskInfo = json.loads(
            redisObject.get(taskKey)
        )
        if taskInfo['complete'] == True: # 任务已完成
            return {
                'success': True,
                'complete': True,
                'checkId': checkId,
                'result': taskInfo['result']
            }

        completeNum = 0 # 测试完成数目
        for tag in taskInfo['proxy']:
            if redisObject.keys(redisPrefix + 'result-' + tag) != []: # 暂未测试
                completeNum += 1
        if completeNum < len(taskInfo['proxy']): # 测试未完成
            return {
                'success': True,
                'complete': False,
                'checkId': checkId,
                'schedule': format(completeNum / len(taskInfo['proxy']), '.2f')
            }

        checkResult = []
        for tag in taskInfo['proxy']: # 遍历检测结果
            checkResult.append(
                json.loads(
                    redisObject.get(redisPrefix + 'result-' + tag)
                )
            )
            redisObject.delete(redisPrefix + 'result-' + tag) # 删除测试结果
        taskInfo['complete'] = True
        taskInfo['result'] = checkResult
        redisObject.set(taskKey, json.dumps(taskInfo)) # 记入数据库
        return {
            'success': True,
            'complete': True,
            'checkId': checkId,
            'result': taskInfo['result']
        }
    except:
        return genError('server error')

def deleteTask(checkId): # 删除任务
    try:
        taskKey = redisObject.keys(redisPrefix + 'task-' + checkId)
        if taskKey == []: # 任务ID不存在
            return genError('invalid check id')
        taskKey = str(taskKey[0], encoding = 'utf-8')
        taskInfo = json.loads(
            redisObject.get(taskKey)
        )
        if taskInfo['complete'] != True: # 任务未完成
            return genError('task not complete')
        redisObject.delete(taskKey)
        return {
            'success': True,
            'checkId': checkId
        }
    except:
        return genError('server error')

@api.route(apiPath + '/check', methods = ['GET','POST'])
def apiCheck():
    if request.method == 'GET':
        return getCheckList()
    elif request.method == 'POST':
        return newCheckTask()

@api.route(apiPath + '/check/<checkId>', methods = ['GET','DELETE'])
def apiCheckId(checkId):
    if request.method == 'GET':
        return getTaskInfo(checkId)
    elif request.method == 'DELETE':
        return deleteTask(checkId)

redisObject = redis.StrictRedis(
    db = 0,
    host = redisHost,
    port = redisPort
)
api.run(host = '0.0.0.0', port = 43581, debug = True)
