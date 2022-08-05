#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
xxObject = {  # a dict that describe multi-field
    'field_1': {
        'optional': ...,  # field force require or not
        'default': ...,  # default value when field is not exist (optional == True)
        'allowNone': ...,  # whether the value can be None (override the format and filter process)
        'type': ...,  # type of field content (in filter process) (python type / dict)
        'multiSub': ...,  # whether there are multi subObject (type is dict)
        'indexKey': ...,  # index key of subObject (type is dict and multiSub == True)
        'format': ...,  # format function (before filter process) (invalid content -> throw error)
        'filter': ...,  # filter function -> bool (throw error when return False)
        'errMsg': ...,  # raise message if there is something error
    },
    'field_2': {
        ...
    },
    ...
}


default value
  + optional: False
  + default: None
  + allowNone: False
  + format: lambda -> return same thing
  + type: force require
  + multiSub: False
  + indexKey: 'type'
  + filter: lambda -> return True
  + errMsg: 'filter error'


pre process
  => field not exist
    => optional == False -> throw errMsg
    => optional == True -> set as default value -> continue
  => field exist
    => filed is None
      => allowNone is False -> throw errMsg
      => allowNone is True -> break
    => field is not None -> continue

format process -> set as field value (maybe throw error -> catch and throw errMsg)

filter process
  => type is `python type` -> compare with field type -> filter function check
  => type is dict
    => multiSub == False -> recursive check
    => multiSub == True
      => field content is not dict or not include indexKey -> throw error
      => others
        => indexKey's content not in type (dict) -> throw error
        => others -> recursive check

"""
