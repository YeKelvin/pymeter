#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : value_replacer
# @Time    : 2019/3/15 9:47
# @Author  : KelvinYe
from sendanywhere.engine.util.compound_variable import CompoundVariable
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class ValueTransformer:
    REF_PREFIX = '${'
    REF_SUFFIX = '}'

    def __init__(self, variables: dict = None):
        self.variables = variables

    def transform_value(self, source) -> str:
        raise NotImplementedError()


class UndoFunctionReplacement(ValueTransformer):
    """替换字符串中的 Function函数
    """

    def transform_value(self, source: str) -> str:
        master_function = CompoundVariable()
        master_function.set_parameters(source)
        return master_function.execute()


class UndoVariableReplacement(ValueTransformer):
    """替换字符串中的 Variable变量
    """

    def transform_value(self, source: str) -> str:
        for key, value in self.variables.items():
            source = source.replace(self.REF_PREFIX + key + self.REF_SUFFIX, value)
        return source


class ValueReplacer:
    def __init__(self, variables: dict = None):
        self.variables = variables
        self.__function_replacer = UndoFunctionReplacement()
        self.__variable_replacer = UndoVariableReplacement(variables)

    def replace_values(self, source: str) -> str:
        return self.__variable_replacer.transform_value(source)

    def replace_functions(self, source: str) -> str:
        return self.__function_replacer.transform_value(source)
