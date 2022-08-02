#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from Basis.Logger import logging
from Basis.Functions import hostFormat


def httpPing(taskId: str, url: str, socksAddr: str, socksPort: int, timeout: int) -> float:
    try:
        startTime = time.time_ns()  # request start time
        socksProxy = 'socks5://%s:%i' % (hostFormat(socksAddr, v6Bracket = True), socksPort)
        logging.debug('[%s] Http ping -> request %s via %s' % (taskId, url, socksProxy))
        httpRequest = requests.get(url, proxies = {  # send http request by socks5 proxy
            'http': socksProxy,
            'https': socksProxy,
        }, timeout = timeout)
    except:  # something error on request process (timeout or proxy not working)
        logging.debug('[%s] Http ping -> request error' % taskId)
        return -1
    if httpRequest.status_code not in range(200, 300):  # http code not 2xx
        logging.debug('[%s] Http ping -> status code %i not expected' % (taskId, httpRequest.status_code))
        return -1
    delay = (time.time_ns() - startTime) / (10 ** 6)  # ns -> ms
    logging.debug('[%s] Http ping -> delay %f ms' % (taskId, delay))
    return round(delay, 2)  # two decimal places


def check(taskId: str, socksInfo: dict, options: dict) -> dict:
    # TODO: multi check
    return {  # TODO: just demo
        'delay': httpPing(taskId, options['url'], socksInfo['addr'], socksInfo['port'], options['timeout'])
    }
