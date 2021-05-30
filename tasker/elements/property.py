#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : property.py
# @Time    : 2020/2/16 14:16
# @Author  : Kelvin.Ye
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class BaseProperty:
    def __init__(self, name: str, value: any):
        self.name = name
        self.value = value

    def get_str_value(self) -> str:
        return str(self.value)

    def get_int_value(self) -> int:
        value = self.get_str_value()
        return int(value) if value else 0

    def get_float_value(self) -> float:
        value = self.get_str_value()
        return float(value) if value else 0.00

    def get_bool_value(self) -> bool:
        value = self.get_str_value()
        return True if value.lower() == 'true' else False

    def get_obj_value(self) -> object:
        return self.value

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class FunctionProperty(BaseProperty):
    def __init__(self, name: str, function):
        super().__init__(name, None)
        self.function = function  # type tasker.engine.value_parser.CompoundVariable
        self.cache_value = None

    def get_raw(self):
        return self.function.raw_parameters

    def get_str_value(self):
        if not self.cache_value:
            self.cache_value = self.function.execute()
        return self.cache_value
