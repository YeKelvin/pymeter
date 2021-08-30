#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler.py
# @Time    : 2020/2/13 16:14
# @Author  : Kelvin.Ye
import traceback
from typing import Final
from typing import Optional

import requests

from pymeter.configs.arguments import Arguments
from pymeter.configs.http_config import HTTPHeaderManager
from pymeter.samplers.http_cons import HTTP_STATUS_CODE
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class HTTPSampler(Sampler):

    # 请求URL
    URL: Final = 'HTTPSampler__url'

    # 请求方法
    METHOD: Final = 'HTTPSampler__method'

    # 请求头管理器
    HEADERS: Final = 'HTTPSampler__headers'

    # 请求参数
    PARAMS: Final = 'HTTPSampler__params'

    # 请求主体
    DATA: Final = 'HTTPSampler__data'

    # 请求表单
    FORM: Final = 'HTTPSampler__form'

    # 请求上传文件
    FILES: Final = 'HTTPSampler__files'

    # 请求内容编码
    ENCODING: Final = 'HTTPSampler__encoding'

    # 允许重定向
    ALLOW_REDIRECTS: Final = 'HTTPSampler__allow_redirects'

    # 请求连接超时时间
    CONNECT_TIMEOUT: Final = 'HTTPSampler__connect_timeout'

    # 等待响应超时时间
    RESPONSE_TIMEOUT: Final = 'HTTPSampler__response_timeout'

    @property
    def url(self) -> str:
        return self.get_property_as_str(self.URL)

    @property
    def method(self) -> str:
        return self.get_property_as_str(self.METHOD)

    @property
    def header_manager(self) -> HTTPHeaderManager:
        return self.get_property(self.HEADERS).get_obj()

    @property
    def headers(self) -> dict:
        hm = self.header_manager
        return hm.headers_as_dict if hm else None

    @property
    def params_manager(self) -> Optional[Arguments]:
        return self.get_property(self.PARAMS).get_obj()

    @property
    def params(self) -> dict:
        pm = self.params_manager
        return pm.to_dict() if pm else {}

    @property
    def data(self) -> str:
        return self.get_property_as_str(self.DATA)

    @property
    def form_manager(self) -> Optional[Arguments]:
        return self.get_property(self.FORM).get_obj()

    @property
    def form(self) -> dict:
        fm = self.form_manager
        return fm.to_dict() if fm else {}

    @property
    def files(self) -> str:
        return self.get_property_as_str(self.FILES)

    @property
    def encoding(self) -> str:
        return self.get_property_as_str(self.ENCODING)

    @property
    def allow_redirects(self) -> bool:
        return self.get_property_as_bool(self.ALLOW_REDIRECTS)

    @property
    def connect_timeout(self) -> float:
        return self.get_property_as_float(self.CONNECT_TIMEOUT)

    @property
    def response_timeout(self) -> float:
        return self.get_property_as_float(self.RESPONSE_TIMEOUT)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.sample_remark = self.remark
        result.request_url = self.url
        result.sample_start()
        res = None

        try:
            res = requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                params=self.params,
                data=self.get_data(),
                files=self.files,
                cookies=None,
                timeout=self.get_timeout(),
                allow_redirects=self.allow_redirects
            )

            result.request_data = self.get_payload(res.request.url)
            result.request_headers = dict(res.request.headers)
            result.response_headers = dict(res.headers)
            result.response_data = res.text
            result.response_code = res.status_code
            result.response_message = HTTP_STATUS_CODE.get(res.status_code)
        except Exception:
            result.success = False
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()
            result.calculate_elapsed_time()

        return result

    def get_data(self):
        if (
            self.headers  # noqa
            and 'content-type' in self.headers  # noqa
            and self.headers['content-type'].lower() == 'application/x-www-form-urlencoded'  # noqa
        ):
            return self.form
        else:
            return self.data

    def get_timeout(self) -> Optional[tuple]:
        if not (self.connect_timeout and self.response_timeout):
            return None
        return self.connect_timeout or 0, self.response_timeout or 0

    def get_payload(self, full_url):
        url = f'{self.method} {full_url}'
        payload = ''

        if self.params:
            if self.params:
                payload = '\n\n'
                for name, value in self.params.items():
                    payload = payload + f'{name}={value}\n'
                payload = payload[:-1]

        if self.data:
            payload = f'\n\n{self.data}'

        return url + payload

    def add_test_element(self, el) -> None:
        """@override"""
        if isinstance(el, HTTPHeaderManager):
            self.set_header_manager(el)
        else:
            super().add_test_element(el)

        # if (el instanceof CookieManager) {
        #     setCookieManager((CookieManager) el);
        # } else if (el instanceof CacheManager) {
        #     setCacheManager((CacheManager) el);
        # } else if (el instanceof HeaderManager) {
        #     setHeaderManager((HeaderManager) el);
        # } else if (el instanceof AuthManager) {
        #     setAuthManager((AuthManager) el);
        # } else if (el instanceof DNSCacheManager) {
        #     setDNSResolver((DNSCacheManager) el);
        # } else {
        #     super.addTestElement(el);
        # }

    def set_header_manager(self, new_manager: HTTPHeaderManager):
        header_manager = self.header_manager

        if header_manager:
            new_manager = header_manager.merge(new_manager)

        self.set_property(self.HEADERS, new_manager)
