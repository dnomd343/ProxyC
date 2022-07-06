#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from Builder import Builder
from Basis.Logger import logging

proxy = {
    'type': 'ss',
    'info': {
        'server': '127.0.0.1',
        'port': 12345,
        'passwd': 'dnomd343',
        'method': 'aes-128-ctr',
        'plugin': None
    }
}

client = Builder(proxy)

logging.critical(client.id)
logging.critical(client.proxyType)
logging.critical(client.proxyInfo)
logging.critical(client.socksAddr)
logging.critical(client.socksPort)

time.sleep(5)
logging.critical(client.status())

client.destroy()
logging.critical(client.status())
logging.critical('Client output:\n' + str(client.output))
