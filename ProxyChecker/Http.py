#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import requests

def httpPing(port, url = 'http://gstatic.com/generate_204', timeout = 30):
    try:
        startTime = time.time_ns()
        socks5 = 'socks5://127.0.0.1:' + str(port)
        httpRequest = requests.get(url, proxies = {
            'http': socks5,
            'https': socks5,
        }, timeout = timeout)
        if httpRequest.status_code == 204:
            delay = (time.time_ns() - startTime) / (10 ** 6)
            return round(delay, 2) # 保留小数点后两位
    except: pass
    return -1

def httpCheck(port, url = 'http://gstatic.com/generate_204', timeout = 30):
    result = []
    result.append(httpPing(port, url, timeout / 4))
    result.append(httpPing(port, url, timeout / 2))
    result.append(httpPing(port, url, timeout / 1))
    failNum = 0
    for ret in result:
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
        return False, sum / 2 # 返回成功延迟均值
    else: # 全部成功
        return True, min(min(result[0], result[1]), result[2]) # 返回最低延迟
