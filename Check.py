#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time

import ProxyBuilder as Builder
import ProxyChecker as Checker
import ProxyFilter as Filter

def __loadDir(folderPath: str) -> bool: # 创建文件夹
    try:
        if os.path.exists(folderPath): # 文件 / 文件夹 存在
            if not os.path.isdir(folderPath): # 文件
                return False # 无法创建
        else: # 不存在
            os.makedirs(folderPath) # 递归创建文件夹
        return True # 文件夹正常
    except:
        return False

def __proxyHttpCheck(socksPort: int, httpCheckUrl: str, httpCheckTimeout: float) -> dict or None: # Http检测
    try:
        health, httpDelay = Checker.httpCheck(
            socksPort,
            url = httpCheckUrl,
            timeout = httpCheckTimeout
        )
        if health is None: # 连接失败
            return None
        return {
            'delay': httpDelay,
            'health': health
        }
    except: # 未知错误
        return None

def proxyTest(
        rawInfo: dict,
        startDelay: float = 1,
        workDir: str = '/tmp/ProxyC',
        httpCheckUrl: str = 'http://gstatic.com/generate_204',
        httpCheckTimeout: float = 20) -> dict or None:
    """
    代理检测入口

        程序异常:
            return None

        启动失败:
            return {
                'success': False,
                'info': proxyInfo
            }

        测试完成:
            return {
                'success': True,
                'check': checkResult,
                'info': proxyInfo
            }

    """
    if not __loadDir(workDir): # 工作文件夹无效
        return None
    if 'info' not in rawInfo: # 缺少代理服务器信息
        return None

    client = None
    status, proxyInfo = Filter.filte(rawInfo['info'], isExtra = True)
    if not status: # 输入节点错误
        return {
            'success': False,
            'info': None
        }
    try:
        status, client = Builder.build(proxyInfo, workDir)
    except Exception as reason: # 构建发生错误
        print(str(reason))
        Builder.destroy(client)
        return None
    if not status: # 节点信息有误
        return {
            'success': False,
            'info': proxyInfo
        }

    time.sleep(startDelay) # 延迟等待客户端启动
    try:
        status = Builder.check(client) # 检查客户端状态
    except: # 检测失败
        Builder.destroy(client)
        return None
    if not status: # 客户端异常退出
        Builder.destroy(client)
        return {
            'success': False,
            'info': proxyInfo
        }

    if 'check' not in rawInfo: # 缺少检测项目
        return None
    checkItem = rawInfo['check']
    checkResult = {}
    for item in checkItem:
        if item == 'http': # http检测
            result = __proxyHttpCheck(client['port'], httpCheckUrl, httpCheckTimeout)
        else: # 未知检测项目
            result = None
        if result is None: # 检测出错
            Builder.destroy(client)
            return None
        checkResult[item] = result

    Builder.destroy(client) # 销毁客户端
    return {
        'success': True,
        'check': checkResult,
        'info': proxyInfo
    }
