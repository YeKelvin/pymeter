#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_headers.py
# @Time    : 2020/2/17 15:41
# @Author  : Kelvin.Ye
from sendanywhere.testelement.test_element import ConfigTestElement
from sendanywhere.testelement.test_element import TestElement


class HttpHeader(TestElement):
    HEADER_NAME = 'Header__name'
    HEADER_VALUE = 'Header__value'

    @property
    def key(self):
        return self.get_property_as_str(self.HEADER_NAME)

    @property
    def value(self):
        return self.get_property_as_str(self.HEADER_VALUE)


class HttpHeaderManager(ConfigTestElement):
    HEADERS = 'HeaderManager__headers'

    def __init__(self, name: str = None, comments: str = None):
        super().__init__(name, comments)

    @property
    def headers(self):
        return self.get_property(self.HEADERS)
