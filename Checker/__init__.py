#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Checker import Http

def Checker(taskId: str, checkInfo: dict, socksInfo: dict) -> dict:

    # TODO: ignore checkInfo for now

    httpRet = Http.check(taskId, socksInfo, {
        'url': 'http://baidu.com/',
        'timeout': 20,
    })
    return {
        'http': httpRet  # TODO: just check http delay for now
    }

    # TODO: return check result
