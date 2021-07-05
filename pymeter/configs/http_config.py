#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_config.py
# @Time    : 2020/2/17 15:41
# @Author  : Kelvin.Ye
from pymeter.elements.element import ConfigTestElement
from pymeter.elements.element import TestElement


class HTTPHeader(TestElement):

    # HTTP头部名称
    HEADER_NAME = 'Header__name'

    # HTTP头部值
    HEADER_VALUE = 'Header__value'

    @property
    def name(self):
        return self.get_property_as_str(self.HEADER_NAME)

    @name.setter
    def name(self, value):
        self.set_property(self.HEADER_NAME, value)

    @property
    def value(self):
        return self.get_property_as_str(self.HEADER_VALUE)

    @value.setter
    def value(self, value):
        self.set_property(self.HEADER_VALUE, value)


class HTTPHeaderManager(ConfigTestElement):
    HEADERS = 'HeaderManager__headers'

    @property
    def headers(self):
        return self.get_property(self.HEADERS)
