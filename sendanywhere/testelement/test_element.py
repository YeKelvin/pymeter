#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element.py
# @Time    : 2020/1/24 23:48
# @Author  : Kelvin.Ye


class TestElement:
    running = False
    name = ''
    comment = ''

    def get_property_as_str(self, key: str, default_value: str) -> str:
        pass

    def get_property_as_int(self, key: str, default_value: int) -> int:
        pass

    def get_property_as_bool(self, key: str, default_value: bool) -> bool:
        pass
