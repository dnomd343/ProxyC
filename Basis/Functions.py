#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import uuid
import psutil
import random
import hashlib
from IPy import IP
from Basis.Logger import logging


def md5Sum(data: str, encode: str = 'utf-8') -> str:
    return hashlib.md5(data.encode(encoding = encode)).hexdigest()


def hostFormat(host: str, v6Bracket: bool = False) -> str:
    try:
        ip = IP(host)
        if v6Bracket and ip.version() == 6:
            return '[%s]' % str(ip)  # [IPv6]
        return str(ip)  # IPv4 / IPV6
    except:  # not ip address
        return host


def genFlag(length: int = 12) -> str:  # generate random task flag
    flag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            flag += chr(tmp + 87) # a ~ f
        else:
            flag += str(tmp) # 0 ~ 9
    logging.debug('Generate new flag -> ' + flag)
    return flag


def genUUID() -> str:  # generate uuid v5
    return str(uuid.uuid5(
        uuid.NAMESPACE_DNS, genFlag(length = 16)
    ))


def getAvailablePort(rangeStart: int = 1024, rangeEnd: int = 65535, waitTime: int = 10) -> int:  # get available port
    if rangeStart > rangeEnd or rangeStart < 1 or rangeEnd > 65535:
        raise RuntimeError('Invalid port range')
    while True:
        port = random.randint(rangeStart, rangeEnd)  # choose randomly
        if checkPortStatus(port):
            logging.debug('Get new port -> %i' % port)
            return port
        time.sleep(waitTime / 1000)  # ms -> s (default 10ms)


def checkPortStatus(port: int) -> bool:  # check if the port is occupied
    for connection in networkStatus():  # scan every connections
        if connection['local']['port'] == port:  # port occupied (whatever ipv4-tcp / ipv4-udp / ipv6-tcp / ipv6-udp)
            logging.debug('Check port %i -> occupied' % port)
            return False
    logging.debug('Check port %i -> available' % port)
    return True


def networkStatus() -> list:  # get all network connections
    result = []
    for connection in psutil.net_connections():
        if not connection.family.name.startswith('AF_INET'):  # AF_INET / AF_INET6
            continue
        if connection.type.name not in ['SOCK_STREAM', 'SOCK_DGRAM']:  # TCP / UDP
            continue
        result.append({
            'fd': connection.fd,
            'family': 'ipv6' if connection.family.name[-1] == '6' else 'ipv4',  # ip version
            'type': 'tcp' if connection.type.name == 'SOCK_STREAM' else 'udp',  # tcp or udp
            'local': {  # local bind address
                'addr': connection.laddr.ip,
                'port': connection.laddr.port,
            },
            'remote': {  # remote address
                'addr': connection.raddr.ip,
                'port': connection.raddr.port,
            } if len(connection.raddr) != 0 else None,
            'status': connection.status,
            'pid': connection.pid,  # process id
        })
    logging.debug('Network status -> found %i connections' % len(result))
    return result


def toInt(raw) -> int:
    pass


def toStr(raw) -> str:
    pass


def toBool(raw) -> bool:
    pass


def isHost(raw) -> bool:
    pass


def isPort(raw) -> bool:
    pass
