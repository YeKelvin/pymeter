#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : property.py
# @Time    : 2020/2/16 14:16
# @Author  : Kelvin.Ye
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PyMeterProperty:
    def __init__(self, name: str, value: any = None):
        self.name = name
        self.value = value

    def get_str(self) -> str:
        raise NotImplementedError

    def get_int(self) -> int:
        raise NotImplementedError

    def get_float(self) -> float:
        raise NotImplementedError

    def get_bool(self) -> bool:
        raise NotImplementedError

    def get_obj(self) -> object:
        raise NotImplementedError


class BasicProperty(PyMeterProperty):

    def get_str(self) -> str:
        return str(self.value)

    def get_int(self) -> int:
        value = self.get_str()
        return int(value) if value else 0

    def get_float(self) -> float:
        value = self.get_str()
        return float(value) if value else 0.00

    def get_bool(self) -> bool:
        value = self.get_str()
        return True if value.lower() == 'true' else False

    def get_obj(self) -> object:
        return self.value

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class NoneProperty(PyMeterProperty):
    def __init__(self, name: str):
        super().__init__(name, None)

    def get_str(self) -> str:
        return ''

    def get_int(self) -> int:
        return 0

    def get_float(self) -> float:
        return 0.00

    def get_bool(self) -> bool:
        return False

    def get_obj(self) -> None:
        return None


class CollectionProperty(PyMeterProperty):
    ...


class ElementProperty(PyMeterProperty):
    ...


class FunctionProperty(PyMeterProperty):
    def __init__(self, name: str, function):
        super().__init__(name, None)
        self.function = function  # type pymeter.engine.value_parser.CompoundVariable
        self.cache_value = None

    def get_raw(self):
        return self.function.raw_parameters

    def get_str(self):
        if not self.cache_value:
            self.cache_value = self.function.execute()
        return self.cache_value
