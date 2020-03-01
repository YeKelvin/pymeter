#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element.py
# @Time    : 2020/1/24 23:48
# @Author  : Kelvin.Ye
from sendanywhere.configs.config import ConfigElement
from sendanywhere.engine.util import ValueReplacer
from sendanywhere.testelement.property import SenderProperty
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class TestElement:
    # 组件的名称
    LABEL = 'TestElement.label'

    # 组件的备注
    COMMENTS = 'TestElement.comments'

    def __init__(self, name: str = None, comments: str = None, propertys: dict = None):
        self.__propertys: {str, SenderProperty} = {}
        if name:
            self.set_name(name)
        if comments:
            self.set_comments(comments)
        if propertys:
            for key, value in propertys.items():
                self.set_property(key, value)

        self.context = None
        self.coroutine_name = None

    @property
    def name(self):
        return self.get_property_as_str(self.LABEL)

    @property
    def comments(self):
        return self.get_property_as_str(self.COMMENTS)

    def set_name(self, name: str):
        self.set_property(self.LABEL, name)

    def set_comments(self, comments: str):
        self.set_property(self.COMMENTS, comments)

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


class ConfigTestElement(TestElement, ConfigElement):
    pass
