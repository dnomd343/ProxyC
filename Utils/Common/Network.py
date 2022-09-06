#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import psutil
import random
from Utils.Logger import logger


def getAvailablePort(rangeStart: int = 1024, rangeEnd: int = 65535, msWait: int = 10) -> int:  # found a available port
    if rangeStart > rangeEnd or rangeStart < 1 or rangeEnd > 65535:  # port range check
        raise RuntimeError('Invalid port range')
    while True:
        port = random.randint(rangeStart, rangeEnd)  # choose randomly
        if isVacantPort(port):
            logger.debug('Found new available port -> %i' % port)
            return port
        time.sleep(msWait / 1000)  # ms -> s (default 10ms)


def isVacantPort(port: int) -> bool:  # whether the port is occupied
    for connection in networkStatus():  # scan every connections
        if connection['local']['port'] == port:  # port occupied (ipv4-tcp / ipv4-udp / ipv6-tcp / ipv6-udp)
            logger.debug('Check port %i -> occupied' % port)
            return False
    logger.debug('Check port %i -> available' % port)  # vacant port
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
    logger.debug('Network status -> found %i connections' % len(result))
    return result
