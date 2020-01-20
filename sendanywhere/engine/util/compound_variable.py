#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : compound_variable
# @Time    : 2020/1/20 14:50
# @Author  : Kelvin.Ye
from sendanywhere.engine.util.function_parser import FunctionParser
from sendanywhere.functions import Function
from sendanywhere.utils.class_finder import ClassFinder
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class CompoundVariable:
    functions =

    def __init__(self, parameters: str = None):
        self.function_parser = FunctionParser()
        self.raw_parameters = None
        self.has_function = False
        self.is_dynamic = False
        self.compiled_components = []
        if parameters:
            self.set_parameters(parameters)

    @staticmethod
    def __init_functions():
        functions = {}
        classes = ClassFinder.find_subclasses(Function)
        for clazz in classes:
            reference_key = clazz.reference_key
            if reference_key:
                functions[reference_key] = clazz
        return functions

    def set_parameters(self, parameters: str):
        self.raw_parameters = parameters
        self.compiled_components = self.function_parser.compile_str(parameters)
