#!/usr/bin/env python3
# -*- coding: utf-8 -*-

filterObject = {
    'optional': {
        'optional': True,  # `optional` is not force require
        'default': False,  # disable `optional` option in default
        'allowNone': False,  # `optional` couldn't be None
        'type': bool,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `optional` key'
    },
    'default': {
        'optional': True,  # `default` is not force require
        'default': None,
        'allowNone': True,  # `default` can be None
        'type': any,  # skip type check
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `default` key'
    },
    'allowNone': {
        'optional': True,  # `allowNone` is not force require
        'default': False,  # disable `allowNone` option in default
        'allowNone': False,  # `allowNone` couldn't be None
        'type': bool,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `allowNone` key'
    },
    'type': {
        'optional': False,  # `type` is force require
        'allowNone': False,  # `type` couldn't be None
        'type': [any, type, list, dict],
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `type` key'
    },
    'multiSub': {
        'optional': True,  # `multiSub` is not force require
        'default': False,  # disable `multiSub` option in default
        'allowNone': False,  # `multiSub` couldn't be None
        'type': bool,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `multiSub` key'
    },
    'indexKey': {
        'optional': True,  # `indexKey` is not force require
        'default': 'type',
        'allowNone': False,  # `indexKey` couldn't be None
        'type': str,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `indexKey` key'
    },
    'format': {
        'optional': True,  # `format` is not force require
        'default': lambda x: x,  # don't change anything
        'allowNone': False,  # `format` couldn't be None
        'type': any,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `format` key'
    },
    'filter': {
        'optional': True,  # `filter` is not force require
        'default': lambda x: True,  # always pass filter
        'allowNone': False,  # `filter` couldn't be None
        'type': any,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `filter` key'
    },
    'errMsg': {
        'optional': True,  # `errMsg` is not force require
        'default': 'filter error',
        'allowNone': False,  # `errMsg` couldn't be None
        'type': str,
        'format': lambda x: x,  # return same value
        'filter': lambda b: True,  # always return True
        'errMsg': 'Invalid `errMsg` key'
    },
}
