#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class buildException(Exception):  # build exception
    def __init__(self, reason):
        self.reason = reason


class filterException(Exception):  # filter exception
    def __init__(self, reason):
        self.reason = reason


class processException(Exception):  # process exception
    def __init__(self, reason):
        self.reason = reason


class managerException(Exception):  # manager exception
    def __init__(self, reason):
        self.reason = reason


class checkException(Exception):  # check exception
    def __init__(self, reason):
        self.reason = reason


class decodeException(Exception):  # url exception
    def __init__(self, reason):
        self.reason = reason
