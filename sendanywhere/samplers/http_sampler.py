#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler.py
# @Time    : 2020/2/13 16:14
# @Author  : Kelvin.Ye
import requests

from sendanywhere.samplers.http_cons import STATUS_CODES
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler


class HTTPSampler(Sampler):
    domain = ''
    port = ''
    protocol = ''
    encoding = ''
    path = ''
    method = ''
    follow_redirects = ''
    auto_redirects = ''
    keepalive = True
    do_multipart_post = ''
    embedded_url_re = ''
    connect_timeout = 0
    response_timeout = 0

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = ''
        result.request_headers = ''
        result.request_data = ''
        result.sample_start()
        res = requests.request('GET',
                               'https://httpbin.org/get',
                               headers=None,
                               params=None,
                               data=None,
                               cookies=None,
                               files=None,
                               timeout=None,
                               allow_redirects=True)
        result.sample_end()
        result.success = True
        result.response_headers = res.headers
        result.response_data = res.text
        result.response_code = res.status_code
        result.response_message = STATUS_CODES.get(res.status_code)

        return result

    def __get_url__(self):
        return ''
