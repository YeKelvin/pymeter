#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : compound_variable
# @Time    : 2020/1/20 14:50
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger
from sendanywhere.functions.function import FUNCTIONS_STORE

log = get_logger(__name__)


class CompoundVariable:
    functions = FUNCTIONS_STORE

    def __init__(self, parameters: str = None):
        from sendanywhere.engine.util import FunctionParser
        self.function_parser = FunctionParser()
        self.raw_parameters = None
        self.has_function = False
        self.is_dynamic = False
        self.compiled_components = []
        if parameters:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: str):
        self.raw_parameters = parameters
        self.compiled_components = self.function_parser.compile_str(parameters)

    @classmethod
    def get_named_function(cls, func_name):
        if func_name in cls.functions:
            return cls.functions[func_name]()
