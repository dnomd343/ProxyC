#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import compileall
from Basis.Logger import logging


def startCompile(dirRange: str = '/') -> None:
    for optimize in [-1, 1, 2]:
        logging.warning('start python compile -> %s (optimize = %i)' % (dirRange, optimize))
        compileall.compile_dir(dirRange, quiet = 1, maxlevels = 256, optimize = optimize)
