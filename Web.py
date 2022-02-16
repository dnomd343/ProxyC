#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request

apiPath = '/'
api = Flask(__name__)

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

def genError(message: str): # 生成JSON错误回复
    return {
        'success': False,
        'message': message
    }

def getAllTask(): # 获取当前所有检测任务
    # TODO: redis query
    return [
        '54cd9ba3a8e86f93',
        'f43c9bae21ae8693',
    ]

def getCheckList(): # 获取检测任务列表
    if request.args.get('token') != accessToken: # token无效
        return genError('invalid token')
    return {
        'success': True,
        'taskList': getAllTask()
    }

def newCheckTask(): # 新增检测任务
    if httpPostArg('token') != accessToken: # token无效
        return genError('invalid token')

    priority = httpPostArg('priority') # 优先级选项
    if not 'priority' in ['a','b','c','d','e']:
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
    
    # TODO: decode and filter
    # TODO: save to redis and generate checkId

    return {
        'success': True,
        'checkId': '233'
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

api.run(host = '0.0.0.0', port = 43581, debug = True)
