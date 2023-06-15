#!/usr/bin python3
# @File    : http_sampler.py
# @Time    : 2020/2/13 16:14
# @Author  : Kelvin.Ye
import traceback
from typing import Final
from typing import Optional

import httpx
from httpx import Response
from loguru import logger

from pymeter.configs.arguments import Arguments
from pymeter.configs.httpconfigs import HTTPHeaderManager
from pymeter.configs.httpconfigs import SessionManager
from pymeter.samplers.http_constants import HTTP_STATUS_CODE
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler


class HTTPSampler(Sampler):

    # 请求类型
    REQUEST_TYPE: Final = 'HTTP'

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

    # 跟随重定向
    FOLLOW_REDIRECTS: Final = 'HTTPSampler__follow_redirects'

    # 请求连接超时时间
    CONNECT_TIMEOUT: Final = 'HTTPSampler__connect_timeout'

    # 等待响应超时时间
    RESPONSE_TIMEOUT: Final = 'HTTPSampler__response_timeout'

    # 运行策略
    RUNNING_STRATEGY: Final = 'HTTPSampler__running_strategy'

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
            headers[name] = (value or '').encode(encoding=self.encoding)
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
    def follow_redirects(self) -> bool:
        return self.get_property_as_bool(self.FOLLOW_REDIRECTS)

    @property
    def connect_timeout(self) -> float:
        return self.get_property_as_float(self.CONNECT_TIMEOUT)

    @property
    def response_timeout(self) -> float:
        return self.get_property_as_float(self.RESPONSE_TIMEOUT)

    def __init__(self, name: str = None):
        super().__init__(name=name)
        self.session_manager = None
        self.content_type = None

    def sample(self) -> SampleResult:  # sourcery skip: extract-method
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
                impl = httpx

            res: Response = impl.request(
                method=self.method,
                url=self.url,
                headers=self.encoded_headers,
                params=self.query_params,
                data=self.get_body(),
                files=self.files,
                cookies=None,
                timeout=self.get_timeout(),
                follow_redirects=self.follow_redirects
            )
            res.encoding = self.encoding

            logger.debug(f'HTTP REQUEST: {self.method} {res.url}\n{res.request.content.decode(self.encoding)}')
            logger.debug(f'HTTP RESPONSE: {res.text}')

            result.request_data = self.get_payload(res)
            result.request_headers = self.decode_headers(dict(res.request.headers))
            result.response_data = res.text or res.status_code
            result.response_code = res.status_code
            result.response_message = HTTP_STATUS_CODE.get(res.status_code)
            result.response_headers = dict(res.headers)
            result.response_cookies = dict(res.cookies)
            # http响应码400以上为错误
            result.success = res.status_code < 400
        except Exception:
            result.error = True
            result.success = False
            result.request_data = result.request_data or self.get_payload_on_error()
            result.request_headers = result.request_headers or self.headers
            result.response_data = traceback.format_exc()
            result.response_message = 'PyMeterException'
        finally:
            result.sample_end()

        return result

    def get_body(self) -> bytes:
        if self.is_www_form_urlencoded():
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

        if body := res.request.content:
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

        if self.is_www_form_urlencoded() and (form_params := self.form_params):
            payload = f'{url}\n\n{self.method} DATA:\n'
            for name, value in form_params.items():
                payload = f'{payload}{name}={value}&'
            return payload[:-1]

        return f'{url}\n\n{self.method} DATA:\n{data}' if (data := self.data) else url

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

    def get_content_type(self):
        if not self.content_type:
            if ct := self.headers.get('content-type'):
                self.content_type = ct.lower()
        return self.content_type

    def is_www_form_urlencoded(self):
        content_type = self.get_content_type()
        return 'x-www-form-urlencoded' in content_type if content_type else False

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
