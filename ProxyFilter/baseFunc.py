#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import IPy
import copy


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


def toInt(raw) -> int: # change to int
    if isinstance(raw, (int, float)): # int / float -> int
        return int(raw)
    elif isinstance(raw, bytes): # bytes -> str
        raw = str(raw, encoding = 'utf-8')
    elif not isinstance(raw, str):
        raise Exception('type not allowed')
    try:
        return int(raw)
    except:
        raise Exception('not a integer')


def toStr(raw) -> str: # change to str
    if raw is None:
        return ''
    elif isinstance(raw, str):
        return raw
    elif isinstance(raw, bytes):
        return str(raw, encoding='utf-8')
    else:
        raise Exception('type not allowed')


def toBool(raw) -> bool: # change to bool
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int):
        raw = str(raw)
    elif isinstance(raw, bytes):
        raw = str(raw, encoding='utf-8')
    elif not isinstance(raw, str):
        raise Exception('type not allowed')
    raw = raw.strip().lower()
    if raw == 'true':
        return True
    elif raw == 'false':
        return False
    else:
        try:
            raw = int(raw)
            return raw != 0
        except:
            raise Exception('not a boolean')


def toStrTidy(raw) -> str: # change to str with trim and lower
    return toStr(raw).strip().lower()


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

        allowNone = False
        if 'allowNone' in option and option['allowNone']: # 允许为None
            allowNone = True

        if not (data[key] is None and allowNone): # 忽略允许None且为None的情况
            if 'format' in option: # 预处理数据
                try:
                    data[key] = option['format'](data[key])
                except Exception as reason:
                    raise filterException('Illegal `' + keyName + '`: ' + str(reason)) # 格式化错误

        # 检查value类型
        if data[key] is None: # 值为None
            if not allowNone: # 不允许为None
                raise filterException('Unexpected None in `' + keyName + '`')
            result[key] = None
        else:
            dataValue = copy.deepcopy(data[key])
            if isinstance(option['type'], (str, list)) and not isinstance(dataValue, dict): # 子对象下必为dict
                raise filterException('Illegal `' + keyName + '`: should be dictionary')
            if isinstance(option['type'], str): # 单子对象
                result[key] = __dictCheck(dataValue, objectList, objectList[option['type']], keyName) # 检查子对象
            elif isinstance(option['type'], list): # 多子对象
                subResult = None
                errMsg = None
                for valueType in option['type']: # 遍历子Object
                    try:
                        subResult = __dictCheck(dataValue, objectList, objectList[valueType], keyName) # 尝试检查子对象
                    except filterException as reason:
                        errMsg = str(reason) # 捕获抛出信息
                    except:
                        continue
                    else: # 子对象匹配成功
                        break
                if subResult is None: # 无匹配子级
                    if errMsg is not None: # 存在子级异常信息
                        raise filterException(errMsg)
                    raise filterException('Error in `' + keyName + '` option')
                result[key] = subResult
            elif not isinstance(data[key], option['type']): # 类型不匹配
                raise filterException('Illegal `' + keyName + '` option')
            else: # 检查无误
                result[key] = dataValue

        if result[key] is not None: # allowNone为False
            if 'filter' in option:
                errFlag = False
                try:
                    if not option['filter'](result[key]): # 格式检查
                        errFlag = True
                except:
                    raise filterException('Filter error in `' + keyName + '`')
                else:
                    if errFlag:
                        if 'indexKey' in option and option['indexKey']:
                            raise Exception('Filter index key')
                        raise filterException(option['errMsg'])
    return result


def __ruleCheck(ruleSet: dict) -> None: # 规则集合法性检查
    if 'rootObject' not in ruleSet: # 根对象检查
        raise Exception('Miss root object')
    for objName in ruleSet: # 遍历全部对象
        if objName[-6:] != 'Object': # 对象名必须以Object结尾
            raise Exception('Illegal object name `' + objName + '`')
        for key, option in ruleSet[objName].items():
            keyName = '`' + objName + '.' + key + '`'
            if 'optional' not in option or not isinstance(option['optional'], bool): # optional检查
                raise Exception('Illegal optional in ' + keyName)
            if not option['optional'] and 'default' not in option: # optional为False时应有default
                raise Exception('Miss default value in ' + keyName)

            allowNone = False
            if 'allowNone' in option and not isinstance(option['allowNone'], bool):
                raise Exception('Illegal allowNone in ' + keyName)
            if 'allowNone' in option and option['allowNone']:
                allowNone = True

            if 'type' not in option: # type值缺失
                raise Exception('Miss type in ' + keyName)
            if not isinstance(option['type'], (type, str, list)): # type为变量类型 / str / list
                raise Exception('Illegal type in ' + keyName)
            if isinstance(option['type'], str) and option['type'] not in ruleSet: # 子Object未定义
                raise Exception('Object `' + option['type'] + '` not found in ' + keyName)
            if isinstance(option['type'], list):
                for subObjName in option['type']:
                    if not isinstance(subObjName, str):
                        raise Exception('Type list must be str in ' + keyName)
                    if subObjName not in ruleSet: # 子Object未定义
                        raise Exception('Object `' + subObjName + '` not found in ' + keyName)

            if 'default' in option:
                if option['default'] is None: # default值检查
                    if not allowNone:
                        raise Exception(keyName + ' can\'t be None')
                else:
                    if isinstance(option['type'], type): # type
                        if not isinstance(option['default'], option['type']):
                            raise Exception('Error default type in ' + keyName)
                    else: # str / list
                        if not isinstance(option['default'], dict):
                            raise Exception('Default type should be dict in ' + keyName)

            if 'format' in option and not callable(option['format']): # format必须为函数
                raise Exception('Format option must be a function in ' + keyName)
            if isinstance(option['type'], type) and 'format' not in option: # 指定变量类型时需有format函数
                raise Exception('Miss format in ' + keyName)

            if 'filter' in option:
                if 'errMsg' not in option: # filter与errMsg同时存在
                    raise Exception('Miss errMsg option in ' + keyName)
                if not callable(option['filter']): # filter必须为函数
                    raise Exception('Filter option must be a function in ' + keyName)
                if not isinstance(option['type'], type):
                    raise Exception('Overage filter option in ' + keyName)
            if 'errMsg' in option and not isinstance(option['errMsg'], str): # errMsg必须为str
                raise Exception('Error message must be str in ' + keyName)

            if 'indexKey' in option and not isinstance(option['indexKey'], bool): # indexKey必为bool
                raise Exception('Illegal indexKey in ' + keyName)


def ruleFilter(rawData: dict, ruleSet: dict, header: dict) -> tuple[bool, dict or str]:
    """
    使用规则集检查原始数据

        原始数据错误:
            return False, {reason}

        原始数据无误:
            return True, {dist}
    """
    try:
        __ruleCheck(ruleSet) # 检查规则集
    except Exception as reason:
        return False, 'Filter rules -> ' + str(reason) # 规则集有误

    data = copy.deepcopy(rawData)
    try:
        data = __dictCheck(data, ruleSet, ruleSet['rootObject'], '') # 开始检查
    except filterException as reason: # 节点格式错误
        return False, str(reason)
    except:
        return False, 'Format error'
    else:
        return True, {**header, **data}
