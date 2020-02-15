#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_result.py
# @Time    : 2020/1/24 23:35
# @Author  : Kelvin.Ye
import time


class SampleResult:
    DEFAULT_ENCODING = ''
    OK_CODE = ''
    OK_MSG = ''

    def __init__(self):
        self.parent = None  # SampleResult
        self.sample_label = None

        self.request_headers = None
        self.request_data = None

        self.response_headers = None
        self.response_data = None
        self.response_code = None
        self.response_message = None

        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

        self.success = None

        self.bytes = None
        self.headers_size = None
        self.body_size = None

        self.stop_test = None
        self.stop_test_now = None
        self.stop_thread = None

    def sample_start(self):
        self.start_time = time.time()

    def sample_end(self):
        self.end_time = time.time()


if __name__ == '__main__':
    print(time.time())
