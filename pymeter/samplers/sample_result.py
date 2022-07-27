#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_result.py
# @Time    : 2020/1/24 23:35
# @Author  : Kelvin.Ye
import traceback
from typing import Optional

from pymeter.tools.advanced import transform
from pymeter.utils import json_util
from pymeter.utils import time_util
from pymeter.utils.json_util import from_json
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class SampleResult:

    default_encoding = 'UTF-8'

    def __init__(self):
        self.parent = None

        self.sample_name = None
        self.sample_remark = None

        self.request_url = None
        self.request_headers = None
        self.request_data = None

        self.response_code = None
        self.response_message = None
        self.response_headers = None
        self.response_cookies = None
        self.response_data = None

        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0
        self.idle_time = 0
        self.pause_time = 0
        self.connect_time = 0

        self.success = True
        self.retrying = False
        self.error = False
        self.assertions = []
        self.sub_results = []

        self.request_headers_size = 0
        self.request_data_size = 0
        self.request_size = 0

        self.response_headers_size = 0
        self.response_data_size = 0
        self.response_size = 0

        self.stop_group = False
        self.stop_test = False
        self.stop_test_now = False

    @property
    def json(self) -> Optional[str]:
        if self.error:
            return None

        # noinspection PyBroadException
        try:
            obj = from_json(self.response_data)
            return transform(obj)
        except Exception:
            log.debug(traceback.format_exc())
            return None

    @property
    def started(self) -> bool:
        return self.start_time != 0

    @property
    def serialization(self) -> dict:
        return {
            'samplerName': self.sample_name,
            'samplerRemark': self.sample_remark,
            'url': self.request_url,
            'request': self.request_data,
            'requestHeaders': self.request_headers,
            'response': self.response_data,
            'responseHeaders': self.response_headers,
            'responseCode': self.response_code,
            'responseMessage': self.response_message,
            'requestSize': self.request_size,
            'responseSize': self.response_size,
            'success': self.success,
            'startTime': time_util.timestamp_to_strftime(self.start_time),
            'endTime': time_util.timestamp_to_strftime(self.end_time),
            'elapsedTime': self.elapsed_time,
            'assertions': [str(assertion) for assertion in self.assertions],
            'subResults': [result.serialization for result in self.sub_results]
        }

    def sample_start(self):
        self.start_time = time_util.timestamp_now()

    def sample_end(self):
        self.end_time = time_util.timestamp_now()
        self.elapsed_time = int(self.end_time * 1000) - int(self.start_time * 1000)

    def add_sub_result(self, subresult: 'SampleResult'):
        if not subresult:
            return

        # Extend the time to the end of the added sample
        self.end_time = max(self.end_time, subresult.end_time)

        # Include the byte count for the added sample
        self.request_headers_size = self.request_headers_size + subresult.request_headers_size
        self.request_data_size = self.request_data_size + subresult.request_data_size
        self.request_size = self.request_size + subresult.request_size

        self.response_headers_size = self.response_headers_size + subresult.response_headers_size
        self.response_data_size = self.response_data_size + subresult.response_data_size
        self.response_size = self.response_size + subresult.response_size

        self.sub_results.append(subresult)
        subresult.parent = self

    def json_path(self, xpath, choice=False, index=None):
        return json_util.json_path(self.response_data, xpath, choice, index)
