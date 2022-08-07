#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from colorlog import ColoredFormatter
from Basis.Constant import LogLevel, LogFile

logLevel = {  # log level
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}[LogLevel.lower()]
dateFormat = '%Y-%m-%d %H:%M:%S'  # log date format
logFormat = '[%(asctime)s] [%(levelname)s] %(message)s (%(module)s.%(funcName)s)'  # log format

logging.basicConfig(
    level = logLevel,
    format = logFormat,
    datefmt = dateFormat,
    filename = LogFile,
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
