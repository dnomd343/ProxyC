#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import compileall
from Basis.Logger import logging


def startCompile(dirRange: str = '/') -> None:
    for optimize in [-1, 1, 2]:
        compileall.compile_dir(dirRange, quiet = 1, maxlevels = 256, optimize = optimize)
        logging.warning('Python optimize compile -> %s (level = %i)' % (dirRange, optimize))
