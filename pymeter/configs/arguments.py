#!/usr/bin python3
# @File    : arguments.py
# @Time    : 2021-07-05 13:44:20
# @Author  : Kelvin.Ye
from typing import List

from pymeter.elements.element import ConfigTestElement
from pymeter.elements.element import TestElement
from pymeter.elements.property import ElementProperty


class Argument(TestElement):

    # 参数名称
    ARGUMENT_NAME = 'Argument__name'

    # 参数值
    ARGUMENT_VALUE = 'Argument__value'

    # 参数描述
    ARGUMENT_DESCRIPTION = 'Argument__desc'

    # 参数元数据，其实就是输出str时用来连接name和value的符号，e.g. name=value
    ARGUMENT_CONNECTOR = 'Argument__connector'

    def __init__(self, name: str = None, value: str = None, desc: str = None, connector: str = '='):
        super().__init__()
        self.name = name
        self.value = value
        self.desc = desc
        self.connector = connector

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
    def connector(self):
        return self.get_property_as_str(self.ARGUMENT_CONNECTOR)

    @connector.setter
    def connector(self, value):
        self.set_property(self.ARGUMENT_CONNECTOR, value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            '{'
            f'  "name"{self.connector}"{self.name}", '
            f'  "value"{self.connector}"{self.value}", '
            f'  "desc"{self.connector}"{self.desc}"'
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

    def add_argument(self, arg: Argument):
        prop = ElementProperty(arg.name, arg)
        if self.running_version:
            self.set_temporary(prop)
        self.arguments.append(arg)

    def add(self, name=None, value=None, desc=None, connector='='):
        self.add_argument(Argument(name, value, desc, connector))

    def to_dict(self) -> dict:
        return {arg.name: arg.value for arg in self.arguments}

    def clear(self):
        self.arguments.clear()
