#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import colorlog
from Utils.Constant import LogLevel, LogFile

logColor = {  # log color
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

logLevel = {  # log level
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}[LogLevel.lower()]

dateFormat = '%Y-%m-%d %H:%M:%S'
timeFormat = '%(asctime)s.%(msecs)03d'
logFormat = '[%(levelname)s] %(message)s (%(module)s.%(funcName)s:%(lineno)d)'

# load fileHandler -> log file
fileHandler = logging.FileHandler(LogFile, encoding = 'utf-8')
fileHandler.setFormatter(logging.Formatter(
    '[' + timeFormat + '] ' + logFormat,
    datefmt = dateFormat
))
fileHandler.setLevel(logging.DEBUG)  # debug level for log file

# load stdHandler -> stderr
stdHandler = colorlog.StreamHandler()
stdHandler.setFormatter(colorlog.ColoredFormatter(
    '%(light_black)s' + timeFormat + '%(log_color)s ' + logFormat,
    datefmt = dateFormat,
    log_colors = logColor,
    stream = sys.stderr
))
stdHandler.setLevel(logLevel)  # custom level for stderr

logger = logging.getLogger()
logger.addHandler(stdHandler)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)  # set log level in handler
