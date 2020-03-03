#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_result.py
# @Time    : 2020/1/24 23:35
# @Author  : Kelvin.Ye
import time


class SampleResult:
    default_encoding = 'UTF-8'

    def __init__(self):
        self.parent = None
        self.sample_label = None

        self.request_headers = None
        self.request_body = None

        self.response_headers = None
        self.response_data = None
        self.response_code = None
        self.response_message = None

        self.start_time = 0
        self.end_time = 0
        self.idle_time = 0
        self.pause_time = 0
        self.connect_time = 0

        self.is_successful = True
        self.assertion_results = []

        self.bytes = None
        self.headers_size = None
        self.body_size = None

        self.is_stop_coroutine = False
        self.is_stop_test = False
        self.is_stop_test_now = False

    @property
    def elapsed_time(self) -> str:
        return f'{self.end_time - self.start_time} ms'

    def sample_start(self):
        self.start_time = int(time.time() * 1000)

    def sample_end(self):
        self.end_time = int(time.time() * 1000)
