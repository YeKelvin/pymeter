#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element.py
# @Time    : 2020/1/24 23:48
# @Author  : Kelvin.Ye
from copy import deepcopy
from typing import Dict

from pymeter.elements.property import BaseProperty
from pymeter.elements.property import NoneProperty
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class ConfigElement:
    """Interface"""
    ...


class TestElement:
    # 组件名称
    LABEL = 'TestElement__label'

    # 组件备注
    REMARK = 'TestElement__remark'

    def __init__(self):
        self.properties: Dict[str, BaseProperty] = {}
        self.context = None
        self.running = False

    @property
    def name(self):
        return self.get_property_as_str(self.LABEL)

    @property
    def remark(self):
        return self.get_property_as_str(self.REMARK)

    @name.setter
    def name(self, name: str) -> None:
        self.set_property(self.LABEL, name)

    @remark.setter
    def remark(self, remark: str) -> None:
        self.set_property(self.REMARK, remark)

    def set_property(self, key: str, value: any) -> None:
        if key and value:
            self.add_property(key, BaseProperty(key, value))

    def add_property(self, key: str, prop: BaseProperty) -> None:
        self.properties[key] = prop

    def get_property(self, key: str, default: any = None) -> BaseProperty:
        if default:
            return self.properties.get(key, default)

        return self.properties.get(key, NoneProperty(key))

    def get_property_as_str(self, key: str, default: str = None) -> str:
        prop = self.get_property(key)
        return default if prop is None or isinstance(prop, NoneProperty) else prop.get_str()

    def get_property_as_int(self, key: str, default: int = None) -> int:
        prop = self.get_property(key)
        return default if prop is None or isinstance(prop, NoneProperty) else prop.get_int()

    def get_property_as_float(self, key: str, default: float = None) -> float:
        prop = self.get_property(key)
        return default if prop is None or isinstance(prop, NoneProperty) else prop.get_float()

    def get_property_as_bool(self, key: str, default: bool = None) -> bool:
        prop = self.get_property(key)
        return default if prop is None or isinstance(prop, NoneProperty) else prop.get_bool()

    def add_test_element(self, element: 'TestElement') -> None:
        """merge in"""
        for key, value in element.items():
            self.add_property(key, value)

    def clear_test_element_children(self) -> None:
        """清除所有使用 #add_test_element(TestElement) 方法合并的元素的属性"""
        ...

    def list(self):
        return list(self.properties.keys())

    def items(self):
        return self.properties.items()

    def clone(self) -> 'TestElement':
        """克隆副本，如果子类有 property以外的属性，请在子类重写该方法
        """
        cloned_element = self.__class__()
        cloned_element.properties = deepcopy(self.properties)
        return cloned_element

    def clear(self):
        """清空属性"""
        self.properties.clear()


class ConfigTestElement(TestElement, ConfigElement):

    def __init__(self):
        TestElement.__init__(self)
        ConfigElement.__init__(self)
