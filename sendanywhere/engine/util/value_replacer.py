#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : value_replacer
# @Time    : 2019/3/15 9:47
# @Author  : Kelvin.Ye
from sendanywhere.engine.util.compound_variable import CompoundVariable
from sendanywhere.testelement.property import BaseProperty
from sendanywhere.testelement.property import FunctionProperty
from sendanywhere.utils.log_util import get_logger


log = get_logger(__name__)


class ValueReplacer:
    @staticmethod
    def replace_values(key: str, source: str) -> BaseProperty:
        master_function = CompoundVariable()
        master_function.set_parameters(source)
        if master_function.has_function:
            return FunctionProperty(key, master_function)
        return BaseProperty(key, source)
