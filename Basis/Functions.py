#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import socket
from Basis.Logger import logging


def genFlag(length: int = 12) -> str:  # generate random task flag
    flag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            flag += chr(tmp + 87) # a ~ f
        else:
            flag += str(tmp) # 0 ~ 9
    logging.debug('generate new flag -> ' + flag)
    return flag


def getAvailablePort(rangeStart: int = 41952, rangeEnd: int = 65535) -> int:  # get a available port
    if rangeStart > rangeEnd or rangeStart < 1 or rangeEnd > 65535:
        raise RuntimeError('invalid port range')
    while True:
        port = random.randint(rangeStart, rangeEnd)  # choose randomly
        if checkPortStatus(port):
            logging.debug('get new port -> %i' % port)
            return port
        time.sleep(0.1) # wait for 100ms


def checkPortStatus(port: int) -> bool:  # check if the port is occupied
    ipv4Tcp = None
    ipv4Udp = None
    ipv6Tcp = None
    ipv6Udp = None
    try:
        ipv4Tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipv4Udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ipv4Tcp.bind(('0.0.0.0', port))
        ipv4Udp.bind(('0.0.0.0', port))
        ipv4Tcp.close()
        ipv4Udp.close()
        ipv6Tcp = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        ipv6Udp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        ipv6Tcp.bind(('::', port))
        ipv6Udp.bind(('::', port))
        ipv6Tcp.close()
        ipv6Udp.close()
        logging.debug('check status of port %i -> available' % port)
        return True  # IPv4 TCP / IPv4 UDP / IPv6 TCP / IPv6 UDP are normal
    except:
        logging.debug('check status of port %i -> occupied' % port)
        return False
    finally:  # close socket
        try:
            ipv4Tcp.close()
        except: pass
        try:
            ipv4Udp.close()
        except: pass
        try:
            ipv6Tcp.close()
        except: pass
        try:
            ipv6Udp.close()
        except: pass
