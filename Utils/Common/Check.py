#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from IPy import IP


def isHost(host: str) -> bool:
    return isIpAddr(host) or isDomain(host)  # IPv4 / IPv6 / Domain


def isPort(port: int) -> bool:
    if type(port) != int:
        return False
    return port in range(1, 65536)  # 1 ~ 65535


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
