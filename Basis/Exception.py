#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class buildException(Exception):  # for build error
    def __init__(self, reason):
        self.reason = reason


class filterException(Exception):  # for filter error
    def __init__(self, reason):
        self.reason = reason
