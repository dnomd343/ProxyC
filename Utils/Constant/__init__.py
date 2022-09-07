#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from Utils.Constant.Plugin import *
from Utils.Constant.Others import *
from Utils.Constant.Default import *
from Utils.Constant.Shadowsocks import *

# Create WorkDir
try:
    os.makedirs(WorkDir)  # just like `mkdir -p ...`
except:
    pass  # folder exist or target is another thing
