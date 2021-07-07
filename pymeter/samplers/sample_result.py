#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_result.py
# @Time    : 2020/1/24 23:35
# @Author  : Kelvin.Ye
from pymeter.utils import time_util


class SampleResult:
    default_encoding = 'UTF-8'

    def __init__(self):
        self.parent = None
        self.sample_name = None
        self.sample_remark = None

        self.request_url = None
        self.request_headers = None
        self.request_data = None

        self.response_headers = None
        self.response_data = None
        self.response_code = None
        self.response_message = None

        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = None
        self.idle_time = 0
        self.pause_time = 0
        self.connect_time = 0

        self.success = True
        self.assertion_results = []

        self.request_headers_size = None
        self.request_data_size = None
        self.request_size = None

        self.response_headers_size = None
        self.response_data_size = None
        self.response_size = None

        self.is_stop_coroutine = False
        self.is_stop_test = False
        self.is_stop_test_now = False

    @property
    def started(self):
        return self.start_time != 0

    def sample_start(self):
        self.start_time = time_util.timestamp_now()

    def sample_end(self):
        self.end_time = time_util.timestamp_now()

    def calculate_elapsed_time(self):
        """计算耗时"""
        self.elapsed_time = f'{int(self.end_time * 1000) - int(self.start_time * 1000)}ms'
