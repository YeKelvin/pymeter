#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : value_replacer
# @Time    : 2019/3/15 9:47
# @Author  : Kelvin.Ye
from sendanywhere.engine.util.compound_variable import CompoundVariable
from sendanywhere.testelement.property import FunctionProperty, SenderProperty
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


# class ValueTransformer:
#     REF_PREFIX = '${'
#     REF_SUFFIX = '}'
#
#     def __init__(self, variables: dict = None):
#         self.variables = variables
#
#     def transform_value(self, source) -> str:
#         raise NotImplementedError()


# class UndoVariableReplacement(ValueTransformer):
#     """替换字符串中的 Variable变量
#     """
#
#     def transform_value(self, source: str) -> str:
#         for key, value in self.variables.items():
#             source = source.replace(self.REF_PREFIX + key + self.REF_SUFFIX, value)
#         return source

class ReplaceStrWithFunctions:
    """替换字符串中的 Function函数
    """

    @staticmethod
    def transform_value(key: str, source: str) -> SenderProperty:
        master_function = CompoundVariable()
        master_function.set_parameters(source)
        if master_function.has_function:
            return FunctionProperty(key, master_function)
        return SenderProperty(key, source)


class ValueReplacer:
    @staticmethod
    def replace_values(key: str, source: str) -> SenderProperty:
        return ReplaceStrWithFunctions.transform_value(key, source)
