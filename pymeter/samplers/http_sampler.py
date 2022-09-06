#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler.py
# @Time    : 2020/2/13 16:14
# @Author  : Kelvin.Ye
import traceback
from typing import Final
from typing import Optional

import requests
from requests.models import Response

from pymeter.configs.arguments import Arguments
from pymeter.configs.httpconfigs import HTTPHeaderManager
from pymeter.configs.httpconfigs import SessionManager
from pymeter.samplers.http_constants import HTTP_STATUS_CODE
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
        return hm.headers_as_dict if hm else {}

    @property
    def encoded_headers(self) -> dict:
        headers = self.headers
        for name, value in headers.items():
            headers[name] = value.encode(encoding=self.encoding)
        return headers

    @property
    def query_params_manager(self) -> Optional[Arguments]:
        return self.get_property(self.PARAMS).get_obj()

    @property
    def query_params(self) -> dict:
        pm = self.query_params_manager
        return pm.to_dict() if pm else {}

    @property
    def form_params_manager(self) -> Optional[Arguments]:
        return self.get_property(self.DATA).get_obj()

    @property
    def form_params(self) -> dict:
        fm = self.form_params_manager
        return fm.to_dict() if fm else {}

    @property
    def data(self) -> str:
        return self.get_property_as_str(self.DATA)

    @property
    def files(self) -> str:
        return self.get_property_as_str(self.FILES)

    @property
    def encoding(self) -> str:
        return self.get_property_as_str(self.ENCODING) or 'utf-8'

    @property
    def allow_redirects(self) -> bool:
        return self.get_property_as_bool(self.ALLOW_REDIRECTS)

    @property
    def connect_timeout(self) -> float:
        return self.get_property_as_float(self.CONNECT_TIMEOUT)

    @property
    def response_timeout(self) -> float:
        return self.get_property_as_float(self.RESPONSE_TIMEOUT)

    def __init__(self, name: str = None):
        super().__init__(name=name)
        self.session_manager = None

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.sample_remark = self.remark
        result.request_url = self.url
        result.sample_start()

        # noinspection PyBroadException
        try:
            if self.session_manager and self.session_manager.session:
                impl = self.session_manager.session
            else:
                impl = requests

            res = impl.request(
                method=self.method,
                url=self.url,
                headers=self.encoded_headers,
                params=self.query_params,
                data=self.get_body_data(),
                files=self.files,
                cookies=None,
                timeout=self.get_timeout(),
                allow_redirects=self.allow_redirects
            )
            res.encoding = self.encoding

            result.request_headers = self.decode_headers(dict(res.request.headers))
            result.request_data = self.get_payload(res)
            result.response_code = res.status_code
            result.response_message = HTTP_STATUS_CODE.get(res.status_code)
            result.response_headers = dict(res.headers)
            result.response_cookies = res.cookies.get_dict()
            result.response_data = res.text
        except Exception:
            result.success = False
            result.error = True
            result.request_headers = result.request_headers or self.headers
            result.request_data = result.request_data or self.get_payload_on_error()
            result.response_message = 'PyMeterException'
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()

        return result

    def get_body_data(self):
        if self.is_x_www_form_urlencoded():
            return self.urlencode(self.form_params)
        elif data := self.data:
            return data.encode(encoding=self.encoding)
        else:
            return None

    def get_timeout(self) -> Optional[tuple]:
        return (
            (self.connect_timeout or 0, self.response_timeout or 0)
            if (self.connect_timeout and self.response_timeout)
            else None
        )

    def get_payload(self, res: Response):
        # res.url 是转码后的值，如果包含中文，就看不懂了，因为这里是为了展示数据
        url = f'{self.method} {self.url}'
        payload = ''

        if query_params := self.query_params:
            query = ''
            for name, value in query_params.items():
                query = f'{query}{name}={value}&'
            url = f'{url}?{query[:-1]}'

        if body := res.request.body:
            body = body.decode(encoding=self.encoding) if isinstance(body, bytes) else body
            payload = f'\n\n{self.method} DATA:\n{body}'

        return url + payload

    def get_payload_on_error(self):
        url = f'{self.method} {self.url}'

        if query_params := self.query_params:
            query = f'{url}?'
            for name, value in query_params.items():
                query = f'{query}{name}={value}&'
            url = f'{url}?{query[:-1]}'

        if self.is_x_www_form_urlencoded() and (form_params := self.form_params):
            payload = f'{url}\n\n{self.method} DATA:\n'
            for name, value in form_params.items():
                payload = f'{payload}{name}={value}&'
            return payload[:-1]

        if data := self.data:
            return f'{url}\n\n{self.method} DATA:\n{data}'

        return url

    def add_test_element(self, el) -> None:
        """@override"""
        if isinstance(el, HTTPHeaderManager):
            self.set_header_manager(el)
        elif isinstance(el, SessionManager):
            self.set_session_manager(el)
        else:
            super().add_test_element(el)

    def set_header_manager(self, new_manager: HTTPHeaderManager):
        if header_manager := self.header_manager:
            new_manager = header_manager.merge(new_manager)

        self.set_property(self.HEADERS, new_manager)

    def set_session_manager(self, manager: SessionManager):
        self.session_manager = manager

    def is_x_www_form_urlencoded(self):
        headers = self.headers
        return (
            headers  # noqa
            and 'content-type' in headers  # noqa
            and headers['content-type'].lower() == 'application/x-www-form-urlencoded'  # noqa
        )

    def urlencode(self, params: dict):
        payload = []
        first = True
        for name, value in params.items():
            if first:
                first = False
            else:
                payload.append('&')
            payload.extend((name, '=', value))
        return ''.join(payload).encode(encoding=self.encoding)

    def decode_headers(self, headers):
        for name, value in headers.items():
            headers[name] = value.decode(encoding=self.encoding) if isinstance(value, bytes) else value
        return headers
