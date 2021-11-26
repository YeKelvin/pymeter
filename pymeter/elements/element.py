#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element.py
# @Time    : 2020/1/24 23:48
# @Author  : Kelvin.Ye
from collections import deque
from copy import deepcopy
from typing import Deque
from typing import Dict
from typing import Iterable
from typing import Optional

from pymeter.elements.property import BasicProperty
from pymeter.elements.property import CollectionProperty
from pymeter.elements.property import DictProperty
from pymeter.elements.property import ElementProperty
from pymeter.elements.property import MultiProperty
from pymeter.elements.property import NoneProperty
from pymeter.elements.property import PyMeterProperty
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class ConfigElement:
    """Interface"""
    ...


class TestElement:

    # 组件名称
    NAME = 'TestElement__name'

    # 组件备注
    REMARK = 'TestElement__remark'

    def __init__(self, name: str = None):
        self.properties = {}  # type: Dict[str, PyMeterProperty]
        self.temporary_properties = None  # type: Optional[Deque]
        self.context = None
        self._running_version = False
        if name:
            self.set_property(self.NAME, name)

    @property
    def name(self) -> str:
        return self.get_property_as_str(self.NAME)

    @property
    def remark(self) -> str:
        return self.get_property_as_str(self.REMARK)

    @name.setter
    def name(self, name: str) -> None:
        self.set_property(self.NAME, name)

    @remark.setter
    def remark(self, remark: str) -> None:
        self.set_property(self.REMARK, remark)

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        # log.debug(f'set running version:[ {running} ] in TestElement:[ {self} ]')
        self._running_version = running
        for prop in self.property_iterator():
            prop.running_version = running

    def recover_running_version(self) -> None:
        # log.debug(f'recover running version in TestElement:[ {self} ]')
        for prop in list(self.properties.values()):
            if self.is_temporary(prop):
                self.remove_property(prop.name)
                self.clear_temporary(prop)
            else:
                prop.recover_running_version(self)

        self.empty_temporary()

    def set_property(self, key: str, value: any) -> None:
        if key:
            if isinstance(value, TestElement):
                self.add_property(key, ElementProperty(key, value))
            elif isinstance(value, list):
                self.add_property(key, CollectionProperty(key, value))
            elif isinstance(value, dict):
                self.add_property(key, DictProperty(key, value))
            elif value is None:
                self.add_property(key, NoneProperty(key))
            else:
                self.add_property(key, BasicProperty(key, value))

    def add_property(self, key: str, prop: PyMeterProperty) -> None:
        if self.running_version:
            self.set_temporary(prop)
        else:
            self.clear_temporary(prop)

        self.properties[key] = prop

    def get_property(self, key: str, default: any = None) -> PyMeterProperty:
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

    def remove_property(self, key) -> None:
        self.properties.pop(key)

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

    def property_iterator(self) -> Iterable:
        return self.properties.values()

    def clone(self) -> 'TestElement':
        """克隆副本，如果子类有 property 以外的属性，请在子类重写该方法"""
        cloned_element = self.__class__()
        cloned_element.properties = deepcopy(self.properties)
        cloned_element.running_version = deepcopy(self.running_version)
        for k, p in cloned_element.properties.items():
            log.error(f'{self.name}, {k=}, saved_value={p.saved_value if hasattr(p, "saved_value") else "None"}')
        return cloned_element

    def clear(self) -> None:
        """清空属性"""
        self.properties.clear()

    def is_temporary(self, prop) -> bool:
        if self.temporary_properties is None:
            return False
        else:
            return prop in self.temporary_properties

    def set_temporary(self, prop) -> None:
        if self.temporary_properties is None:
            self.temporary_properties = deque()

        self.temporary_properties.append(prop)
        if isinstance(prop, MultiProperty):
            for prop in prop.iterator():
                self.set_temporary(prop)

    def clear_temporary(self, prop):
        if self.temporary_properties is not None:
            self.temporary_properties.remove(prop)

    def empty_temporary(self):
        if self.temporary_properties is not None:
            self.temporary_properties.clear()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<'{self.name}' ({type(self).__name__} @ {id(self)})>"


class ConfigTestElement(TestElement, ConfigElement):

    def __init__(self):
        TestElement.__init__(self)
        ConfigElement.__init__(self)
