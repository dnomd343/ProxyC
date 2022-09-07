#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import random
import hashlib
from Utils.Logger import logger


def md5Sum(string: str) -> str:
    return hashlib.md5(string.encode(encoding = 'utf-8')).hexdigest()  # md5 hash


def genUUID() -> str:  # generate uuid v5
    return str(uuid.uuid5(
        uuid.NAMESPACE_DNS, genFlag(length = 16)
    ))


def genFlag(length: int = 12) -> str:  # generate random task flag
    flag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            flag += chr(tmp + 87) # a ~ f
        else:
            flag += str(tmp) # 0 ~ 9
    logger.debug('Generate new flag -> %s' % flag)
    return flag
