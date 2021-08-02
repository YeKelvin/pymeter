#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : arguments.py
# @Time    : 2021-07-05 13:44:20
# @Author  : Kelvin.Ye
from typing import List

from pymeter.elements.element import ConfigTestElement
from pymeter.elements.element import TestElement


class Argument(TestElement):

    # 参数名称
    ARGUMENT_NAME = 'Argument__name'

    # 参数值
    ARGUMENT_VALUE = 'Argument__value'

    # 参数描述
    ARGUMENT_DESCRIPTION = 'Argument__desc'

    # 参数元数据，其实就是输出str时用来连接name和value的符号，e.g. name=value
    ARGUMENT_SEPARATOR = 'Argument__separator'

    def __init__(self, name: str = None, value: str = None, desc: str = None, sep: str = '='):
        super().__init__()
        self.name = name
        self.value = value
        self.desc = desc
        self.sep = sep

    @property
    def name(self):
        return self.get_property_as_str(self.ARGUMENT_NAME)

    @name.setter
    def name(self, value):
        self.set_property(self.ARGUMENT_NAME, value)

    @property
    def value(self):
        return self.get_property_as_str(self.ARGUMENT_VALUE)

    @value.setter
    def value(self, value):
        self.set_property(self.ARGUMENT_VALUE, value)

    @property
    def desc(self):
        return self.get_property_as_str(self.ARGUMENT_DESCRIPTION)

    @desc.setter
    def desc(self, value):
        self.set_property(self.ARGUMENT_DESCRIPTION, value)

    @property
    def sep(self):
        return self.get_property_as_str(self.ARGUMENT_SEPARATOR)

    @sep.setter
    def sep(self, value):
        self.set_property(self.ARGUMENT_SEPARATOR, value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            '{'
            f'"name"{self.sep}"{self.name}", '
            f'"value"{self.sep}"{self.value}", '
            f'"desc"{self.sep}"{self.desc}"'
            '}'
        )


class Arguments(ConfigTestElement):

    ARGUMENTS = 'Arguments__arguments'

    def __init__(self):
        super().__init__()
        self.add_property(self.ARGUMENTS, [])

    @property
    def arguments(self) -> List[Argument]:
        return self.get_property(self.ARGUMENTS).get_obj()

    def add(self, arg: Argument):
        self.arguments.append(arg)

    def to_dict(self) -> dict:
        args = {}
        for arg in self.arguments:
            args[arg.name] = arg.value
        return args
