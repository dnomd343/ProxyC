#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def toInt(raw) -> int:
    try:
        return int(raw)
    except:
        raise RuntimeError('Unable convert to int')


def toStr(raw, allowNone: bool = False) -> str:
    if raw is None:
        if allowNone:  # None => 'none'
            return 'none'
        raise RuntimeError('None could not convert to str')
    if isinstance(raw, bytes):  # bytes -> str
        return str(raw, encoding = 'utf-8')
    try:
        return str(raw)
    except:
        raise RuntimeError('Unable convert to str')


def toStrTidy(raw, allowNone: bool = False) -> str:
    return toStr(raw, allowNone).strip().lower()  # with trim and lower


def toBool(raw) -> bool:
    if isinstance(raw, (bool, int, float)):
        return bool(raw)
    try:
        raw = toStr(raw).strip().lower()
        if raw in ['true', 'false']:
            return True if raw == 'true' else False
        return int(raw) != 0
    except:
        raise RuntimeError('Unable convert to bool')
