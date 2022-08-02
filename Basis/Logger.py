#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from colorlog import ColoredFormatter

logFile = 'runtime.log'
logLevel = logging.DEBUG
# logLevel = logging.WARNING
dateFormat = '%Y-%m-%d %H:%M:%S'
logFormat = '[%(asctime)s] [%(levelname)s] %(message)s (%(module)s.%(funcName)s)'
logging.basicConfig(
    level = logLevel,
    format = logFormat,
    datefmt = dateFormat,
    filename = logFile,
)
logHandler = logging.StreamHandler(stream = sys.stdout)
logHandler.setFormatter(ColoredFormatter(
    fmt = '%(log_color)s' + logFormat,
    datefmt = dateFormat,
    log_colors = {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))
logging.getLogger().addHandler(logHandler)


if __name__ == '__main__':
    logging.debug('debug')
    logging.info('info')
    logging.warning('warn')
    logging.error('error')
    logging.critical('critical')
