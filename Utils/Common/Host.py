#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IPy import IP


def v6AddBracket(host: str) -> str:  # add bracket for ipv6
    return hostFormat(host, v6Bracket = True)


def hostFormat(host: str, v6Bracket: bool = False) -> str:
    try:
        if host[:1] == '[' and host[-1:] == ']':  # [IPv6]
            host = host[1:-1]  # remove extra bracket
        ip = IP(host)
        if v6Bracket and ip.version() == 6:
            return '[%s]' % str(ip)  # [IPv6]
        return str(ip)  # IPv4 / IPV6
    except:  # not ip address
        return host
