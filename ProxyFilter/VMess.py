#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import baseFunc

def __vmessFill(raw: dict) -> dict: # 补全可选值
    try:
        pass
    except:
        pass
    return raw

def __vmessFormat(raw: dict) -> dict: # 容错性格式化
    try:
        pass
    except:
        pass
    return raw

def __obfsParamCheck(obfs: dict or None) -> tuple[bool, str or None]: # obfs参数检查
    pass

def __secureParamCheck(secure: dict or None) -> tuple[bool, str or None]: # secure参数检查
    pass

def __streamParamCheck(stream: dict) -> tuple[bool, str or None]: # stream参数检查
    if 'type' not in stream:
        return False, 'Missing `type` option'
    if stream['type'] == 'tcp':
        if 'obfs' not in stream:
            return False, 'Missing `stream.obfs` option'
        if 'secure' not in stream:
            return False, 'Missing `stream.secure` option'

        if (stream['obfs'] is not None) and (not isinstance(stream['obfs'], dict)):
            return False, 'Illegal `stream.obfs` option'
        if (stream['secure'] is not None) and (not isinstance(stream['secure'], dict)):
            return False, 'Illegal `stream.secure` option'

        status, reason = __obfsParamCheck(stream['obfs'])
        if not status:
            return False, reason
        status, reason = __secureParamCheck(stream['secure'])
        if not status:
            return False, reason

    elif stream['type'] == 'kcp':
        if 'seed' not in stream:
            return False, 'Missing `stream.seed` option'
        if 'obfs' not in stream:
            return False, 'Missing `stream.obfs` option'
        if 'secure' not in stream:
            return False, 'Missing `stream.secure` option'
        pass

    elif stream['type'] == 'ws':
        if 'host' not in stream:
            return False, 'Missing `stream.host` option'
        if 'path' not in stream:
            return False, 'Missing `stream.path` option'
        if 'ed' not in stream:
            return False, 'Missing `stream.ed` option'
        if 'secure' not in stream:
            return False, 'Missing `stream.secure` option'
        pass

    elif stream['type'] == 'h2':
        if 'host' not in stream:
            return False, 'Missing `stream.host` option'
        if 'path' not in stream:
            return False, 'Missing `stream.path` option'
        if 'secure' not in stream:
            return False, 'Missing `stream.secure` option'
        pass

    elif stream['type'] == 'quic':
        if 'method' not in stream:
            return False, 'Missing `stream.method` option'
        if 'passwd' not in stream:
            return False, 'Missing `stream.passwd` option'
        if 'obfs' not in stream:
            return False, 'Missing `stream.obfs` option'
        if 'secure' not in stream:
            return False, 'Missing `stream.secure` option'
        pass

    elif stream['type'] == 'grpc':
        if 'service' not in stream:
            return False, 'Missing `stream.service` option'
        if 'secure' not in stream:
            return False, 'Missing `stream.secure` option'
        pass

    else:
        return False, 'Unknown stream type'
    return True, None

def __vmessParamCheck(raw: dict) -> tuple[bool, str or None]: # VMess节点参数检查
    try:
        if 'server' not in raw:
            return False, 'Missing `server` option'
        if 'port' not in raw:
            return False, 'Missing `port` option'
        if 'method' not in raw:
            return False, 'Missing `method` option'
        if 'id' not in raw:
            return False, 'Missing `id` option'
        if 'aid' not in raw:
            return False, 'Missing `aid` option'
        if 'stream' not in raw:
            return False, 'Missing `stream` option'

        if not isinstance(raw['server'], str):
            return False, 'Illegal `server` option'
        if not isinstance(raw['port'], int):
            return False, 'Illegal `port` option'
        if not isinstance(raw['method'], str):
            return False, 'Illegal `method` option'
        if not isinstance(raw['id'], str):
            return False, 'Illegal `id` option'
        if not isinstance(raw['aid'], str):
            return False, 'Illegal `aid` option'
        if not isinstance(raw['stream'], dict):
            return False, 'Illegal `stream` option'

        status, reason = __streamParamCheck(raw['stream'])
        if not status:
            return False, reason
    except:
        return False, 'Unknown error'
    return True, None

def vmessFilter(rawInfo: dict, isExtra: bool) -> tuple[bool, str or dict]:
    """
    VMess节点合法性检查

        不合法:
            return False, {reason}

        合法:
            return True, {
                'type': 'vmess',
                ...
            }
    """
    try:
        raw = rawInfo
        raw = __vmessFormat(__vmessFill(raw))  # 预处理
        status, reason = __vmessParamCheck(raw) # 参数检查
        if not status: # 参数有误
            return False, reason

        result = {'type': 'vmess'}
        if isExtra: # 携带额外参数
            if 'remark' not in raw: # 补全默认值
                raw['remark'] = ''
            if raw['remark'] is None: # 容错格式化
                raw['remark'] = ''
            if not isinstance(raw['remark'], str): # 参数检查
                return False, 'Illegal `remark` option'
            result['remark'] = raw['remark']

        pass
    except:
        return False, 'Unknown error'
    return True, result
