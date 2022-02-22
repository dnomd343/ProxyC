#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import IPy

def isHost(host: str) -> bool:
    """
    判断host是否合法

    IPv4 / IPv6 / Domain

        合法: return True

        不合法: return False
    """
    try:
        IPy.IP(host)
        if host.find('/') != -1: # filter CIDR
            return False
        if host.find('.') == -1 and host.find(':') == -1:
            return False
        return True # IP地址合法
    except:
        pass
    try:
        return re.search( # 域名匹配
            r'^(?=^.{3,255}$)[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62}(\.[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62})+$', host
        ) is not None
    except: # 异常错误
        return False

def isPort(port: int) -> bool:
    """
    判断端口是否合法

    1 ~ 65535

        合法: return True

        不合法: return False
    """
    try:
        if 1 <= port <= 65535: # 1 ~ 65535
            return True
    except: # illegal
        pass
    return False

class filterException(Exception): # 检测异常
    def __init__(self, reason):
        self.reason = reason

def __dictCheck(data: dict, objectList: dict, limitRules: dict, keyPrefix: str) -> dict: # 递归检查dict
    result = {}
    for key, option in limitRules.items(): # 遍历规则
        keyName = key if keyPrefix == '' else keyPrefix + '.' + key

        # 检查必选key 补全可选key
        if key not in data:
            if option['optional']: # 必选
                raise filterException('Missing `' + keyName + '` option') # 必选值缺失
            else: # 可选
                data[key] = option['default'] # 补全可选值

        if 'format' in option: # 预处理
            data[key] = option['format'](data[key])

        # 检查value类型
        if 'allowNone' in option and option['allowNone'] and data[key] is None: # 允许为None且值为None
            result[key] = None
        else:
            if isinstance(option['type'], str):
                result[key] = __dictCheck(data[key], objectList, objectList[option['type']], keyName) # 检查子对象
            elif not isinstance(data[key], option['type']): # 类型不匹配
                raise filterException('Illegal `' + keyName + '` option')
            else:
                result[key] = data[key]

        if 'filter' in option and not option['filter'](data[key]): # 格式检查
            raise filterException(option['errMsg'])
        else:
            result[key] = data[key]
    return result

def rulesFilter(rawData: dict, rulesList: dict) -> tuple[bool, dict or str]:
    """
    规则参数
        optional -> 必选
        default -> optional为False时必选
        type -> 必选
        allowNone -> 可选
        format -> 可选
        filter -> 可选
        errMsg -> filter存在时必选
    """
    data = rawData
    try:
        data = __dictCheck(data, rulesList, rulesList['rootObject'], '') # 开始检查
    except filterException as reason: # 节点格式错误
        return False, str(reason)
    except:
        return False, 'Filter error'
    else:
        return True, data
