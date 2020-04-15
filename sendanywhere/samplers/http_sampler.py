#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler.py
# @Time    : 2020/2/13 16:14
# @Author  : Kelvin.Ye
import traceback

import requests

from sendanywhere.samplers.http_cons import STATUS_CODES
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HTTPSampler(Sampler, TestElement):
    URL = 'HTTPSampler__url'
    ENCODING = 'HTTPSampler__encoding'
    METHOD = 'HTTPSampler__method'
    PARAMS = 'HTTPSampler__params'
    DATA = 'HTTPSampler__data'
    FILES = 'HTTPSampler__files'
    FOLLOW_REDIRECTS = 'HTTPSampler__follow_redirects'
    AUTO_REDIRECTS = 'HTTPSampler__auto_redirects'
    KEEP_ALIVE = 'HTTPSampler__keep_alive'
    CONNECT_TIMEOUT = 'HTTPSampler__connect_timeout'
    RESPONSE_TIMEOUT = 'HTTPSampler__response_timeout'

    @property
    def url(self):
        return self.get_property_as_str(self.URL)

    @property
    def encoding(self):
        return self.get_property_as_str(self.ENCODING)

    @property
    def method(self):
        return self.get_property_as_str(self.METHOD)

    @property
    def params(self):
        return self.get_property_as_str(self.PARAMS)

    @property
    def data(self):
        return self.get_property_as_str(self.DATA)

    @property
    def files(self):
        return self.get_property_as_str(self.FILES)

    @property
    def follow_redirects(self) -> bool:
        return self.get_property_as_bool(self.FOLLOW_REDIRECTS)

    @property
    def auto_redirects(self) -> bool:
        return self.get_property_as_bool(self.AUTO_REDIRECTS)

    @property
    def keep_alive(self) -> bool:
        return self.get_property_as_bool(self.KEEP_ALIVE)

    @property
    def connect_timeout(self) -> float:
        return self.get_property_as_float(self.CONNECT_TIMEOUT)

    @property
    def response_timeout(self) -> float:
        return self.get_property_as_float(self.RESPONSE_TIMEOUT)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.name
        result.request_headers = ''
        result.request_body = self.__get_request_body()
        result.sample_start()
        res = None

        try:
            res = requests.request(method=self.method,
                                   url=self.url,
                                   headers=None,
                                   params=self.params,
                                   data=self.data,
                                   files=self.files,
                                   cookies=None,
                                   timeout=self.__get_timeout(),
                                   allow_redirects=True)
        except Exception:
            result.response_data = traceback.format_exc()

        result.sample_end()
        result.calculate_elapsed_time()

        if res:
            result.response_headers = res.headers
            result.response_data = res.text
            result.response_code = res.status_code
            result.response_message = STATUS_CODES.get(res.status_code)

        return result

    def __get_timeout(self) -> tuple or None:
        if not (self.connect_timeout and self.response_timeout):
            return None
        return self.connect_timeout or 0, self.response_timeout or 0

    def __get_request_body(self):
        if self.params:
            return self.params
        if self.data:
            return self.data
        if self.files:
            return self.files

# if __name__ == '__main__':
#     url = 'http://127.0.0.1/5000/get'
#     encoding = ''
#     method = 'GET'
#     params = '{"aa":"bb","func":"${__Time()}"}'
#     data = '{"cc":"dd","func":"${__Time()}"}'
#     follow_redirects = ''
#     auto_redirects = ''
#     keep_alive = ''
#     connect_timeout = ''
#     response_timeout = ''
#     sample = HTTPSampler()
#     sample.set_property(sample.LABEL, '测试')
#     sample.set_property(sample.DOMAIN, domain)
#     sample.set_property(sample.PORT, port)
#     sample.set_property(sample.PROTOCOL, protocol)
#     sample.set_property(sample.PATH, path)
#     sample.set_property(sample.METHOD, method)
#     sample.set_property(sample.PARAMS, params)
#     result = sample.sample()
#     print(result.__dict__)
