#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import time
from Checker import Checker
from Utils.Logger import logger
from Utils.Common import isVacantPort
from Builder import Builder, clientEntry
from Utils.Exception import checkException


def buildClient(taskId: str, taskInfo: dict) -> Builder:
    try:
        return Builder(
            proxyType = taskInfo['type'],
            proxyInfo = taskInfo['info'],
            bindAddr = '127.0.0.1',  # socks5 exposed host
            taskId = taskId,
        )
    except Exception as reason:
        logger.error('[%s] Client build error -> %s' % (taskId, reason))
        raise checkException('Client build error')


def waitClient(taskId: str, client: Builder, times: int = 150, delay: int = 100):  # wait until client port occupied
    for i in range(times):
        if not isVacantPort(client.socksPort):  # port occupied
            break
        time.sleep(delay / 1000)  # wait in default: 100ms * 150 => 15s
    time.sleep(1)  # wait a short time before check process
    if not client.status():  # client unexpected exit
        logger.warning('[%s] Client unexpected exit' % taskId)
        client.destroy()  # remove file and kill sub process
        logger.debug('[%s] Client output\n%s', (taskId, client.output))
        raise checkException('Client unexpected exit')


def Check(taskId: str, taskInfo: dict) -> dict:
    logger.info('[%s] Start checking process -> %s' % (taskId, taskInfo))
    if taskInfo['type'] not in clientEntry:  # unknown proxy type
        logger.error('[%s] Unknown proxy type %s' % (taskId, taskInfo['type']))
        raise checkException('Unknown proxy type')
    client = buildClient(taskId, taskInfo)  # build proxy client
    logger.info('[%s] Client loaded successfully' % taskId)
    waitClient(taskId, client)  # wait for the client to start
    checkResult = Checker(taskId, taskInfo['check'], {  # start check process
        'addr': client.socksAddr,
        'port': client.socksPort,
    })
    logger.info('[%s] Client check result -> %s' % (taskId, checkResult))
    client.destroy()  # clean up client
    taskInfo = copy.deepcopy(taskInfo)
    taskInfo.pop('check')  # remove check items
    return {
        **taskInfo,
        'success': True,
        'result': checkResult,  # add check result
    }
