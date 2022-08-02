#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from Checker import Http

checkEntry = {
    'http': Http.check
}

def formatCheck(rawInfo: list) -> dict:
    # TODO: format check info
    # TODO: rawInfo -> ['...', {'type': '...', ...}, ...]
    return {
        'http': {
            'times': 3,
            'url': 'http://gstatic.com/generate_204',
            'timeout': 20,
        }
    }


def Checker(taskId: str, checkInfo: dict, socksInfo: dict) -> dict:
    diffItems = {x for x in checkInfo} - {x for x in checkEntry}
    if len(diffItems) != 0:  # include unknown check items
        logging.error('[%s] Unknown check items -> %s' % (taskId, diffItems))
        raise RuntimeError('Unknown check items')
    result = {}
    for checkItem, checkOptions in checkInfo.items():
        result[checkItem] = checkEntry[checkItem](taskId, socksInfo, checkOptions)
    return result
