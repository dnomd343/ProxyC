#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import requests

def httpPing(port, url = 'http://gstatic.com/generate_204', timeout = 30):
    '''
    HTTP请求延迟测试

        检测异常: return None, {reason}

        服务错误: return False, {reason}

        连接正常: return True, httpDelay
    '''
    try:
        startTime = time.time_ns() # 请求开始时间
        socks5 = 'socks5://127.0.0.1:' + str(port)
        httpRequest = requests.get(url, proxies = { # http请求
            'http': socks5,
            'https': socks5,
        }, timeout = timeout)
    except NameError: # 模块无效
        return None, 'Missing modules'
    except requests.exceptions.InvalidSchema: # 缺失pysocks包
        return None, 'Missing dependencies for SOCKS support'
    except requests.exceptions.ConnectTimeout: # 请求超时
        return False, 'Request timeout'
    except requests.exceptions.ReadTimeout: # 请求超时
        return False, 'Request timeout'
    except requests.exceptions.Timeout: # 请求超时
        return False, 'Request timeout'
    except: # 未知错误
        return False, 'Request error'

    try:
        statusCode = httpRequest.status_code # 获取http状态码
    except:
        return None, 'Http request error'
    if 'statusCode' in vars() and statusCode >= 200 and statusCode < 300: # http测试成功
        delay = (time.time_ns() - startTime) / (10 ** 6)
        return True, round(delay, 2) # 保留小数点后两位
    else:
        return False, 'Http status code not 204'

def httpCheck(port, url = 'http://gstatic.com/generate_204', timeout = 30):
    '''
    HTTP请求测试

        测试异常: return None, {reason}

        测试完成: return health, delay
    '''
    result = []
    failNum = 0
    timeout = timeout * 64 / 119 # 4/64 + 2/64 + 1/64 + 1/4 + 1/2 + 1/1
    for i in [4, 2, 1]: # 三次测试
        time.sleep(timeout / 64 * i)
        status, delay = httpPing(port, url, timeout / i)
        if status == None: # 测试异常
            return None, delay
        elif status == False: # 连接失败
            result.append(-1)
        else: # 连接成功
            result.append(delay)
    for ret in result: # 计算失败次数
        if ret < 0:
            failNum += 1

    if failNum == 3: # 全部失败
        return False, -1
    elif failNum == 2: # 仅成功一次
        for ret in result:
            if ret > 0: # 返回成功单次延迟
                return False, ret
    elif failNum == 1: # 存在一次失败
        sum = 0
        for ret in result:
            if ret > 0:
                sum += ret
        return False, round(sum / 2, 2) # 返回成功延迟均值
    else: # 全部成功
        return True, min(min(result[0], result[1]), result[2]) # 返回最低延迟
