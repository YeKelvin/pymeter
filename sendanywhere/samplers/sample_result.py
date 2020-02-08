#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_result.py
# @Time    : 2020/1/24 23:35
# @Author  : Kelvin.Ye


class SampleResult:
    DEFAULT_ENCODING = ''
    OK_CODE = ''
    OK_MSG = ''

    def __init__(self):
        self.parent = None  # SampleResult
        self.label = None

        self.requestHeaders = None
        self.samplerData = None

        self.responseHeaders = None
        self.responseData = None
        self.responseCode = None
        self.responseMessage = None

        self.timeStamp = None
        self.startTime = None
        self.endTime = None
        self.elapsedTime = None

        self.success = None

        self.bytes = None
        self.headersSize = None
        self.bodySize = None

        self.stopTest = None
        self.stopTestNow = None
        self.stopThread = None
