#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis import Constant

Constant.LogLevel = 'DEBUG'

from Utils.Logger import logger

import requests

logger.debug('debug')
logger.info('info')
logger.warning('warning')
logger.error('error')
logger.critical('critical')

requests.get('https://baidu.com')
