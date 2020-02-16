#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element.py
# @Time    : 2020/1/24 23:48
# @Author  : Kelvin.Ye
from sendanywhere.engine.util import ValueReplacer
from sendanywhere.testelement.property import SenderProperty
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class TestElement:
    LABEL = 'TestElement.label'
    COMMENTS = 'TestElement.comments'

    def __init__(self):
        self.__propertys: {str, SenderProperty} = {}

    def set_property(self, key: str, value: any) -> None:
        self.__propertys[key] = ValueReplacer.replace_values(key, value)

    def get_property(self, key: str, default: any = None) -> SenderProperty:
        return self.__propertys.get(key, default)

    def get_raw_property(self, key: str) -> any:
        prop = self.get_property(key)
        return prop.get_raw() if prop else None

    def get_property_as_str(self, key: str, default: str = None) -> str:
        prop = self.get_property(key)
        return prop.get_str_value() if prop else default

    def get_property_as_int(self, key: str, default: int = None) -> int:
        prop = self.get_property(key)
        return prop.get_int_value() if prop else default

    def get_property_as_float(self, key: str, default: float = None) -> float:
        prop = self.get_property(key)
        return prop.get_float_value() if prop else default

    def get_property_as_bool(self, key: str, default: bool = None) -> bool:
        prop = self.get_property(key)
        return prop.get_bool_value() if prop else default
