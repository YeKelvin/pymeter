#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler.py
# @Time    : 2020/2/13 16:14
# @Author  : Kelvin.Ye
import requests

from sendanywhere.samplers.http_cons import STATUS_CODES
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HTTPSampler(Sampler, TestElement):
    DOMAIN = 'HTTPSampler.domain'
    PORT = 'HTTPSampler.port'
    PROTOCOL = 'HTTPSampler.protocol'
    ENCODING = 'HTTPSampler.encoding'
    PATH = 'HTTPSampler.path'
    METHOD = 'HTTPSampler.method'
    PARAMS = 'HTTPSampler.params'
    DATA = 'HTTPSampler.data'
    FILES = 'HTTPSampler.files'
    FOLLOW_REDIRECTS = 'HTTPSampler.follow_redirects'
    AUTO_REDIRECTS = 'HTTPSampler.auto_redirects'
    KEEP_ALIVE = 'HTTPSampler.keep_alive'
    CONNECT_TIMEOUT = 'HTTPSampler.connect_timeout'
    RESPONSE_TIMEOUT = 'HTTPSampler.response_timeout'

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.get_property_as_str(self.LABEL)
        result.request_headers = ''
        result.request_body = self.__get_request_body()
        result.sample_start()
        res = requests.request(method=self.get_property_as_str(self.METHOD),
                               url=self.__get_url(),
                               headers=None,
                               params=self.get_property_as_str(self.PARAMS),
                               data=self.get_property_as_str(self.DATA),
                               files=self.get_property_as_str(self.FILES),
                               cookies=None,
                               timeout=self.__get_timeout(),
                               allow_redirects=True)
        result.sample_end()
        result.is_successful = True
        result.response_headers = res.headers
        result.response_data = res.text
        result.response_code = res.status_code
        result.response_message = STATUS_CODES.get(res.status_code)
        result.calculate_elapsed_time()

        return result

    def __get_url(self) -> str:
        protocol = self.get_property_as_str(self.PROTOCOL)
        domain = self.get_property_as_str(self.DOMAIN)
        port = self.get_property_as_str(self.PORT)
        path = self.get_property_as_str(self.PATH)
        if not path.startswith('/'):
            path = '/' + path
        return f'{protocol}://{domain}:{port}{path}'

    def __get_timeout(self) -> tuple or None:
        connect_timeout = self.get_property_as_float(self.CONNECT_TIMEOUT)
        response_timeout = self.get_property_as_float(self.RESPONSE_TIMEOUT)
        if not (connect_timeout and response_timeout):
            return None
        return connect_timeout or 0, response_timeout or 0

    def __get_request_body(self):
        params = self.get_property_as_str(self.PARAMS)
        data = self.get_property_as_str(self.DATA)
        files = self.get_property_as_str(self.FILES)
        if params:
            return params
        if data:
            return data
        if files:
            return files

# if __name__ == '__main__':
#     domain = '127.0.0.1'
#     port = '5000'
#     protocol = 'http'
#     encoding = ''
#     path = '/get'
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
