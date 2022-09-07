#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IPy import IP
from Utils.Logger import logger
from Utils.Common.Coding import *


def v6AddBracket(host: str) -> str:  # add bracket for ipv6
    return hostFormat(host, v6Bracket = True)


def hostFormat(host: str, v6Bracket: bool = False) -> str:
    try:
        if host[:1] == '[' and host[-1:] == ']':  # [IPv6] format
            host = host[1:-1]  # remove extra bracket
        ip = IP(host)
        if v6Bracket and ip.version() == 6:
            return '[%s]' % str(ip)  # [IPv6]
        return str(ip)  # IPv4 / IPV6
    except:  # not ip address
        return host


def checkScheme(url: str, scheme: str, name: str) -> str:  # check url scheme and remove it
    if not url.startswith('%s://' % scheme):
        logger.warning('%s url should start with `%s://`' % (name, scheme))
        raise RuntimeError('%s scheme error' % name)
    return url[len(scheme) + 3:]


def splitTag(url: str, fromRight: bool = True, spaceRemark: bool = True) -> tuple[str, str]:  # split tag after `#`
    if '#' not in url:  # without tag
        return url, ''
    if not fromRight:
        url, remark = url.split('#', 1)  # from left search
    else:
        url, remark = url.rsplit('#', 1)  # from right search
    if spaceRemark:  # deal with space remark for space
        remark = remark.replace('+', ' ')
    return url, urlDecode(remark)


def splitParam(params: str) -> dict:  # split params
    ret = {}
    if params != '':
        for param in params.split('&'):
            ret[param.split('=', 1)[0]] = urlDecode(param.split('=', 1)[1])
    return ret