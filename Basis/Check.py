#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from Basis.Logger import logging
from Builder import Builder, clientEntry

from ProxyChecker import httpCheck  # TODO: refactor in the future


def Check(proxyType: str, proxyInfo: dict, checkInfo: dict) -> dict:
    # TODO: checkInfo -> [...] (only check http for now)
    if proxyType not in clientEntry:
        logging.error('Unknown proxy type %s' % proxyType)
        raise RuntimeError('Unknown proxy type')
    try:
        client = Builder(proxyType, proxyInfo)
    except Exception as reason:
        logging.error('Client build error -> %s' % reason)
        raise RuntimeError('Client build error')

    # TODO: debug combine output
    logging.debug(client.id)
    logging.debug(client.proxyType)
    logging.debug(client.proxyInfo)
    logging.debug(client.socksAddr)
    logging.debug(client.socksPort)

    # TODO: wait port occupied
    time.sleep(1)
    if not client.status():  # client unexpected exit
        client.destroy()  # remove file and kill sub process
        logging.error('Client unexpected exit\n%s', client.output)
        raise RuntimeError('Client unexpected exit')

    # TODO: check process
    status, _ = httpCheck(client.socksPort)  # TODO: add socks5 addr

    logging.critical('http check status -> %s' % status)

    client.destroy()  # clean up the client

    return {
        'http': {
            'status': status,
            # TODO: more http check info
        },
        # TODO: more check items (from checkInfo list)
    }

