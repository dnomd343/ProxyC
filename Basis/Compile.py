#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import compileall
from Basis.Logger import logging


def startCompile(dirRange: str = '/'):
    for optimize in [-1, 1, 2]:
        logging.warning('start compile -> %s (optimize = %i)' %(dirRange, optimize))
        compileall.compile_dir(dirRange, quiet = 1, maxlevels = 256, optimize = optimize)
