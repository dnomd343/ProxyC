#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Basis.Exception import filterException

filterObject = {
    'optional': {
        'type': bool,
        'optional': True,  # `optional` is not force require
        'default': False,  # disable `optional` option in default
        'allowNone': False,  # `optional` couldn't be None
    },
    'default': {
        'type': any,  # skip type check
        'optional': True,  # `default` is not force require
        'default': None,
        'allowNone': True,  # `default` can be None
    },
    'allowNone': {
        'type': bool,
        'optional': True,  # `allowNone` is not force require
        'default': False,  # disable `allowNone` option in default
        'allowNone': False,  # `allowNone` couldn't be None
    },
    'type': {
        'type': [any, type, list, dict],
        'optional': False,  # `type` is force require
        'allowNone': False,  # `type` couldn't be None
    },
    'multiSub': {
        'type': bool,
        'optional': True,  # `multiSub` is not force require
        'default': False,  # disable `multiSub` option in default
        'allowNone': False,  # `multiSub` couldn't be None
    },
    'indexKey': {
        'type': str,
        'optional': True,  # `indexKey` is not force require
        'default': 'type',
        'allowNone': False,  # `indexKey` couldn't be None
    },
    'format': {
        'type': any,
        'optional': True,  # `format` is not force require
        'default': lambda x: x,  # don't change anything
        'allowNone': False,  # `format` couldn't be None
    },
    'filter': {
        'type': any,
        'optional': True,  # `filter` is not force require
        'default': lambda x: True,  # always pass filter
        'allowNone': False,  # `filter` couldn't be None
    },
    'errMsg': {
        'type': str,
        'optional': True,  # `errMsg` is not force require
        'default': 'Filter error',
        'allowNone': False,  # `errMsg` couldn't be None
    }
}

for field in filterObject:
    filterObject[field]['errMsg'] = 'Invalid `%s` key' % field
    filterObject[field]['format'] = filterObject['format']['default']  # return same value
    filterObject[field]['filter'] = filterObject['filter']['default']  # always return True


def Filter(raw: dict, rules: dict) -> dict:
    if type(raw) != dict:
        raise filterException('Invalid input for filter')
    data = {}
    raw = copy.deepcopy(raw)
    rules = copy.deepcopy(rules)
    for key, rule in rules.items():
        # pretreatment process (raw --[copy / default value]--> data)
        if key not in raw:  # key not exist
            if not rule['optional']:  # force require key not exist
                raise filterException('Missing `%s` field' % key)
            data[key] = rule['default']  # set default value
        else:  # key exist
            data[key] = raw[key]
        # format process (data --[format]--> data)
        if data[key] is None:  # key content is None
            if not rule['allowNone']:  # key is not allow None
                raise filterException('Field `%s` shouldn\'t be None' % key)
            continue  # skip following process
        try:
            data[key] = rule['format'](data[key])  # run format
        except:
            raise filterException(rule['errMsg'])  # format error
        # filter process (data --[type check (& filter check)]--> pass / non-pass)
        if type(rule['type']) == type:  # str / int / bool / ...
            rule['type'] = [rule['type']]  # str -> [str] / int -> [int] / ...
        if type(rule['type']) == list:  # [str, int, bool, ...]
            if data[key] == any and any in rule['type']:  # special case -> skip type filter
                pass
            elif type(data[key]) not in rule['type']:  # type not in allow list
                raise filterException('Invalid `%s` field' % key)
        elif type(rule['type']) == dict:  # check subObject
            if type(data[key]) != dict:
                raise filterException('Invalid sub object in `%s`' % key)  # subObject content should be dict
            if not rule['multiSub']:  # single subObject
                subRules = rule['type']
            else:  # multi subObject
                if rule['indexKey'] not in data[key]:  # confirm index key exist
                    raise filterException('Index key `%s` not found in `%s`' % (rule['indexKey'], key))
                subType = data[key][rule['indexKey']].lower()
                if subType not in rule['type']:  # confirm subObject rule exist
                    raise filterException('Unknown index `%s` in key `%s`' % (subType, key))
                subRules = rule['type'][subType]
            try:
                data[key] = Filter(data[key], subRules)
            except filterException as exp:
                raise filterException('%s (in `%s`)' % (exp, key))  # add located info
            continue
        elif rule['type'] != any:  # type == any -> skip type filter
            raise filterException('Unknown `type` in rules')
        if not rule['filter'](data[key]):  # run filter
            raise filterException(rule['errMsg'])
    return data


def rulesFilter(rules: dict) -> dict:
    result = {}
    for key, rule in rules.items():  # filter by basic rules
        try:
            result[key] = Filter(rule, filterObject)
        except filterException as exp:
            raise filterException('%s (`%s` in rules)' % (exp, key))  # rules error
    return result


filterObject = rulesFilter(filterObject)  # self-format
