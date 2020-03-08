#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element.py
# @Time    : 2020/1/24 23:48
# @Author  : Kelvin.Ye
from copy import deepcopy

from sendanywhere.configs.config import ConfigElement
from sendanywhere.engine.util import ValueReplacer
from sendanywhere.testelement.property import BaseProperty
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class TestElement:
    # 组件的名称
    LABEL = 'TestElement.label'

    # 组件的备注
    COMMENTS = 'TestElement.comments'

    def __init__(self, name: str = None, comments: str = None):
        self.__propertys: {str, BaseProperty} = {}
        self.context = None

        if name:
            self.name = name
        if comments:
            self.comments = comments

    @property
    def name(self):
        return self.get_property_as_str(self.LABEL)

    @property
    def comments(self):
        return self.get_property_as_str(self.COMMENTS)

    @name.setter
    def name(self, name: str) -> None:
        self.set_property(self.LABEL, name)

    @comments.setter
    def comments(self, comments: str) -> None:
        self.set_property(self.COMMENTS, comments)

    def set_property(self, key: str, value: any) -> None:
        if key and value:
            self.add_property(key, BaseProperty(key, value))

    def set_property_by_replace(self, key: str, value: any) -> None:
        if key and value:
            self.add_property(key, ValueReplacer.replace_values(key, value))

    def add_property(self, key: str, prop: BaseProperty) -> None:
        self.__propertys[key] = prop

    def get_property(self, key: str, default: any = None) -> BaseProperty:
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

    def add_test_element(self, element: 'TestElement') -> None:
        """merge in
        """
        for key, value in element.items():
            self.add_property(key, value)

    def clear_test_element_children(self) -> None:
        """此方法应清除所有通过 {@link #add_test_element(TestElement)} 方法合并的测试元素属性
        """
        pass

    def list(self):
        return list(self.__propertys.keys())

    def items(self):
        return self.__propertys.items()

    def clone(self) -> 'TestElement':
        """克隆副本，如果子类有 property以外的属性，请在子类重写该方法
        """
        cloned_element = self.__class__()
        cloned_element.__propertys = deepcopy(self.__propertys)
        return cloned_element


class ConfigTestElement(TestElement, ConfigElement):
    def __init__(self, name: str = None, comments: str = None):
        super().__init__(name, comments)
