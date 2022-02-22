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

def httpPostArg(field: str) -> dict or str or None: # 获取HTTP POST参数
    try:
        if request.values.get(field) is not None: # application/x-www-form-urlencoded
            return request.values.get(field)
        elif request.json.get(field) is not None: # application/json
            return request.json.get(field)
        elif request.form.get(field) is not None: # multipart/form-data
            return request.form.get(field)
    except:
        pass
    return None

def genRandomId(length: int = 24) -> str: # 生成随机ID
    tag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            tag += chr(tmp + 87) # a ~ f
        else:
            tag += str(tmp) # 0 ~ 9
    return tag

def genError(message: str) -> dict: # 生成错误回复
    return {
        'success': False,
        'message': message
    }

def genSuccess(data: dict) -> dict: # 生成成功返回
    data['success'] = True
    return data

def getCheckList(userId: str) -> list or None: # 获取检测任务列表
    try:
        taskList = []
        rawTaskList = redisObject.keys(redisPrefix + 'task-' + userId + '*')
        for task in rawTaskList: # 获取任务ID
            taskList.append(str(task[len(redisPrefix) + 5:], encoding = 'utf-8'))
        return taskList
    except:
        return None

def addCheckTask(checkList: dict, proxyList: dict, priority: str, userId: str) -> dict: # 新增检测任务
    try:
        import ProxyDecoder as Decoder
        import ProxyFilter as Filter

        checkList = list(set(checkList)) # 检测方式去重
        for checkMethod in checkList:
            if checkMethod not in ['http']:
                return genError('unknown check method `' + checkMethod + '`')

        for i in range(0, len(proxyList)):
            proxyList[i] = Decoder.decode(proxyList[i]) # 解码分享链接
            if proxyList[i] is None:
                return genError('could not decode index ' + str(i))
            status, proxyList[i] = Filter.filte(proxyList[i], isExtra = True) # 节点信息检查
            if not status: # 节点不合法
                return genError('index ' + str(i) + ': ' + proxyList[i])

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

        checkId = userId + genRandomId(8) # 24位userId + 8位随机 -> 32位任务ID
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
        return genSuccess({
            'checkId': checkId
        })
    except:
        return genError('server error')

def getTaskInfo(checkId: str) -> dict: # 获取任务详情
    try:
        taskKey = redisObject.keys(redisPrefix + 'task-' + checkId)
        if not taskKey: # 任务ID不存在
            return genError('invalid check id')
        taskKey = str(taskKey[0], encoding = 'utf-8')
        taskInfo = json.loads(
            redisObject.get(taskKey)
        )
        if taskInfo['complete']: # 任务已完成
            return {
                'success': True,
                'complete': True,
                'checkId': checkId,
                'number': len(taskInfo['proxy']),
                'result': taskInfo['result']
            }

        completeNum = 0 # 测试完成数目
        for tag in taskInfo['proxy']:
            if redisObject.keys(redisPrefix + 'result-' + tag): # 暂未测试
                completeNum += 1
        if completeNum < len(taskInfo['proxy']): # 测试未完成
            return {
                'success': True,
                'complete': False,
                'checkId': checkId,
                'number': len(taskInfo['proxy']),
                'schedule': round(completeNum / len(taskInfo['proxy']), 2)
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
            'number': len(taskInfo['proxy']),
            'result': taskInfo['result']
        }
    except:
        return genError('server error')

def deleteTask(checkId: str) -> dict: # 删除任务
    try:
        taskKey = redisObject.keys(redisPrefix + 'task-' + checkId)
        if not taskKey: # 任务ID不存在
            return genError('invalid check id')
        taskKey = str(taskKey[0], encoding = 'utf-8')
        taskInfo = json.loads(
            redisObject.get(taskKey)
        )
        if not taskInfo['complete']: # 任务未完成
            return genError('task not complete')
        redisObject.delete(taskKey)
        return {
            'success': True,
            'checkId': checkId
        }
    except:
        return genError('server error')

def isAdminToken(token: str) -> bool:
    """
    是否为管理员token

        验证成功:
            return True

        验证失败:
            return False
    """
    adminToken = accessToken
    return token == adminToken

def isUserToken(token: str) -> bool:
    """
    是否为有效token

        token有效:
            return True

        token无效:
            return False
    """
    try:
        if token.encode('utf-8') in redisObject.smembers(redisPrefix + 'users'):
            return True
    except:
        pass
    return False

def addUser(priority: str, remain: int or str) -> tuple[bool, str]:
    """
    添加账号

        添加成功:
            return True, userId

        添加异常:
            return False, {reason}
    """
    try:
        userId = genRandomId(length = 24)
        if priority not in ['a', 'b', 'c', 'd', 'e']: # 优先级无效
            return False, 'invalid priority'
        remain = int(remain)
        if remain < 0:
            remain = -1 # 不限次数
        userInfo = {
            'token': userId,
            'priority': priority,
            'remain': remain
        }
        redisObject.sadd( # 添加账号token
            redisPrefix + 'users', userId
        )
        redisObject.set( # 记录账号信息
            redisPrefix + 'user-' + userId,
            json.dumps(userInfo)
        )
        return True, userId # 返回userId
    except:
        return False, 'server error'

def delUser(userId: str) -> tuple[bool, str]:
    """
    删除账号

        删除成功:
            return True, userId

        删除失败:
            return False, {reason}
    """
    try:
        if not isUserToken(userId):
            return False, 'invalid user id'

        taskList = redisObject.keys(redisPrefix + 'task-' + userId + '*')
        if taskList:
            return False, 'task list not empty'

        redisObject.srem(redisPrefix + 'users', userId)
        redisObject.delete(redisPrefix + 'user-' + userId)
        return True, userId
    except:
        return False, 'server error'

def getUserInfo(userId: str, minus: bool = False) -> dict or None:
    """
    获取账号信息 (minus = True: 剩余次数 - 1)

        获取异常:
            return None

        获取成功:
            return {
                'token': '...'
                'priority': '...',
                'remain': ...
            }
    """
    try:
        if not isUserToken(userId): # userId不存在
            return None
        userInfo = json.loads(
            redisObject.get(redisPrefix + 'user-' + userId) # 账号信息
        )
        if minus and userInfo['remain'] > 0:
            userInfo['remain'] -= 1 # 剩余次数 - 1
            redisObject.set(
                redisPrefix + 'user-' + userId, # 记入数据库
                json.dumps(userInfo)
            )
        return userInfo
    except:
        return None # 异常

def getUserList() -> dict or None:
    """
    获取所有账号信息

        获取异常:
            return None

        获取成功:
            return {
                'token_1': {
                    'priority': '...',
                    'working': ...,
                    'remain': ...,
                },
                'token_2': {
                    ...
                }
                ...
            }
    """
    try:
        userList = {}
        for userId in redisObject.smembers(redisPrefix + 'users'): # 遍历全部账号
            userId = str(userId, encoding = 'utf-8')
            userInfo = getUserInfo(userId)
            userInfo.pop('token')
            userList[userId] = userInfo # 记录账号信息
        return userList
    except:
        return None

def modifyUserInfo(userId: str, priority: str = None, remain = None) -> bool:
    """
    修改账号信息

        修改成功:
            return True

        修改失败:
            return False
    """

    try:
        userInfo = getUserInfo(userId)
        if userInfo is None: # 账号不存在
            return False
        if priority is not None: # 优先级变动
            if priority not in ['a', 'b', 'c', 'd', 'e']: # 优先级无效
                return False
            userInfo['priority'] = priority
        if remain is not None: # 剩余次数变动
            remain = int(remain)
            if remain < 0:
                remain = -1 # 不限次数
            userInfo['remain'] = remain
        redisObject.set(
            redisPrefix + 'user-' + userId, # 记录账号信息
            json.dumps(userInfo)
        )
        return True
    except:
        return False

@api.route(apiPath + '/user', methods = ['GET', 'POST'])
def apiUser() -> dict:
    if request.method == 'GET': # 获取账号列表
        if not isAdminToken(request.args.get('token')): # 非管理员token
            return genError('invalid admin token')
        userList = getUserList()
        if userList is None: # 获取失败
            return genError('server error')
        return genSuccess({
            'user': userList
        })
    elif request.method == 'POST': # 添加账号
        if not isAdminToken(httpPostArg('token')): # 非管理员token
            return genError('invalid admin token')
        priority = httpPostArg('priority')
        if priority is None:
            priority = 'c' # 默认优先级
        remain = httpPostArg('remain')
        if remain is None:
            remain = '-1' # 默认剩余次数
        status, userId = addUser(priority, remain) # 创建新账号
        if not status:
            return genError(userId) # 创建错误
        return genSuccess({
            'userId': userId # 创建成功
        })

@api.route(apiPath + '/user/<userId>', methods = ['GET', 'PUT', 'PATCH', 'DELETE'])
def apiUserId(userId: str) -> dict:
    if request.method == 'GET': # 获取账号信息
        userInfo = getUserInfo(userId)
        if userInfo is None:
            return genError('invalid user id')
        return genSuccess(userInfo)
    elif request.method == 'PUT' or request.method == 'PATCH': # 更新账号信息
        if not isAdminToken(httpPostArg('token')): # 非管理员token
            return genError('invalid admin token')
        priority = httpPostArg('priority')
        remain = httpPostArg('remain')
        if request.method == 'PUT':
            if priority is None or remain is None: # 参数不全
                return genError('missing parameter')
        if not modifyUserInfo(userId, priority = priority, remain = remain): # 更新账号信息
            return genError('server error')
        return genSuccess(
            getUserInfo(userId) # 更新成功
        )
    elif request.method == 'DELETE': # 销毁账号
        if not isAdminToken(httpPostArg('token')): # 非管理员token
            return genError('invalid admin token')
        status, reason = delUser(userId)
        if not status:
            return genError(reason)
        return genSuccess({
            'userId': userId # 删除成功
        })

@api.route(apiPath + '/check', methods = ['GET', 'POST'])
def apiCheck() -> dict:
    if request.method == 'GET': # 获取检测任务列表
        token = request.args.get('token')
        if not isUserToken(token):
            return genError('invalid user token')
        taskList = getCheckList(token)
        if taskList is None:
            return genError('server error')
        return genSuccess({
            'taskList': taskList
        })
    elif request.method == 'POST': # 添加检测任务
        token = httpPostArg('token')
        if not isUserToken(token):
            return genError('invalid user token')
        checkList = httpPostArg('check') # 检测列表
        if checkList is None:
            return genError('missing check list')
        proxyList = httpPostArg('proxy') # 代理列表
        if proxyList is None:
            return genError('missing proxy list')
        priority = getUserInfo(token, minus = True)['priority'] # 获取账号优先级
        if priority is None:
            return genError('server error')
        return addCheckTask(checkList, proxyList, priority, token)

@api.route(apiPath + '/check/<checkId>', methods = ['GET', 'DELETE'])
def apiCheckId(checkId: str) -> dict:
    if request.method == 'GET': # 获取检测任务状态
        return getTaskInfo(checkId)
    elif request.method == 'DELETE': # 删除检测任务
        return deleteTask(checkId)

redisObject = redis.StrictRedis(
    db = 0,
    host = redisHost,
    port = redisPort
)
api.run(host = '0.0.0.0', port = 43581, debug = True)
