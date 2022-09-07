#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import uuid
import random
import hashlib

from Utils.Logger import logger


def isIpAddr(ipAddr: str) -> bool:
    try:
        if '/' in ipAddr:  # filter CIDR
            return False
        if '.' not in ipAddr and ':' not in ipAddr:  # not IPv4 or IPv6
            return False
        IP(ipAddr)  # try to convert to IP address
        return True  # valid IP address
    except:
        return False


def isDomain(domain: str) -> bool:
    try:
        domainRegex = r'^(?=^.{3,255}$)[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62}(\.[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62})+$'
        return re.search(domainRegex, domain) is not None  # regex matching
    except:  # unexpected error
        return False


def isHost(host: str) -> bool:
    return isIpAddr(host) or isDomain(host)  # IPv4 / IPv6 / Domain


def isPort(port: int) -> bool:
    if type(port) != int:
        return False
    return port in range(1, 65536)  # 1 ~ 65535


def md5Sum(data: str, encode: str = 'utf-8') -> str:
    return hashlib.md5(data.encode(encoding = encode)).hexdigest()  # MD5 hash


def genFlag(length: int = 12) -> str:  # generate random task flag
    flag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            flag += chr(tmp + 87) # a ~ f
        else:
            flag += str(tmp) # 0 ~ 9
    logger.debug('Generate new flag -> ' + flag)
    return flag


def genUUID() -> str:  # generate uuid v5
    return str(uuid.uuid5(
        uuid.NAMESPACE_DNS, genFlag(length = 16)
    ))


