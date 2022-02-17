#!/usr/bin/python
# -*- coding:utf-8 -*-

import compileall

maxLevels = 256
compileDir = '/usr'
compileall.compile_dir(compileDir, quiet = 1, maxlevels = maxLevels)
compileall.compile_dir(compileDir, quiet = 1, maxlevels = maxLevels, optimize = 1)
compileall.compile_dir(compileDir, quiet = 1, maxlevels = maxLevels, optimize = 2)
