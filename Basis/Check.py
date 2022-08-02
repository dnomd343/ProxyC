#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import time
from Checker import Checker
from Basis.Logger import logging
from Builder import Builder, clientEntry


def buildClient(taskId: str, taskInfo: dict) -> Builder:
    try:
        return Builder(
            proxyType = taskInfo['type'],
            proxyInfo = taskInfo['info'],
            bindAddr = '127.0.0.1',  # socks5 exposed host
            taskId = taskId,
        )
    except Exception as reason:
        logging.error('[%s] Client build error -> %s' % (taskId, reason))
        raise RuntimeError('Client build error')


def waitClient(taskId: str, client: Builder):
    # TODO: wait port occupied (client.socksPort)
    time.sleep(1)  # TODO: simple delay for now
    if not client.status():  # client unexpected exit
        logging.warning('[%s] Client unexpected exit' % taskId)
        client.destroy()  # remove file and kill sub process
        logging.debug('[%s] Client output\n%s', (taskId, client.output))
        raise RuntimeError('Client unexpected exit')


def Check(taskId: str, taskInfo: dict) -> dict:
    logging.info('[%s] Start checking process -> %s' % (taskId, taskInfo))
    if taskInfo['type'] not in clientEntry:  # unknown proxy type
        logging.error('[%s] Unknown proxy type %s' % (taskId, taskInfo['type']))
        raise RuntimeError('Unknown proxy type')
    client = buildClient(taskId, taskInfo)  # build proxy client
    logging.info('[%s] Client loaded successfully' % taskId)
    waitClient(taskId, client)  # wait for the client to start
    checkResult = Checker(taskId, taskInfo['check'], {  # start check process
        'addr': client.socksAddr,
        'port': client.socksPort,
    })
    logging.info('[%s] Client check result -> %s' % (taskId, checkResult))
    client.destroy()  # clean up client
    taskInfo = copy.deepcopy(taskInfo)
    taskInfo.pop('check')  # remove check items
    return {
        **taskInfo,
        'result': checkResult,  # add check result
    }
