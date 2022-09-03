#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class buildException(Exception):  # for build error
    def __init__(self, reason):
        self.reason = reason


class filterException(Exception):  # for filter error
    def __init__(self, reason):
        self.reason = reason


class processException(Exception):  # for process error
    def __init__(self, reason):
        self.reason = reason


class managerException(Exception):  # for manager error
    def __init__(self, reason):
        self.reason = reason


class checkException(Exception):  # for check error
    def __init__(self, reason):
        self.reason = reason


class decodeException(Exception):  # for url decode
    def __init__(self, reason):
        self.reason = reason
