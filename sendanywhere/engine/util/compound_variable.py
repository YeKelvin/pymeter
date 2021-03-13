#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : compound_variable
# @Time    : 2020/1/20 14:50
# @Author  : Kelvin.Ye
from sendanywhere.engine.util.simple_variable import SimpleVariable
from sendanywhere.functions import Function
from sendanywhere.utils.class_finder import ClassFinder
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class CompoundVariable:
    """复合函数
    """
    functions = {}

    def __init__(self, parameters: str = None):
        if not self.functions:
            self.__init_functions__()

        self.raw_parameters = None
        self.has_function = False
        self.is_dynamic = False
        self.compiled_components = []
        self.permanent_results = None  # 缓存函数执行结果
        if parameters:
            self.set_parameters(parameters)

    def execute(self):
        """执行函数
        """
        if not self.is_dynamic and self.permanent_results:  # 优先返回函数执行结果缓存
            log.debug('return cache results')
            return self.permanent_results

        if not self.compiled_components:
            log.debug('compiled component is empty')
            return ''

        results = []
        for item in self.compiled_components:
            if isinstance(item, Function):
                log.debug(f'appending function:[ {item.REF_KEY} ] execution result')
                results.append(item.execute())
            elif isinstance(item, SimpleVariable):
                log.debug(f'appending variable:[ {item.name} ] actual value')
                results.append(item.value)
            else:
                results.append(item)
        results_str = ''.join(results)

        if not self.is_dynamic:
            log.debug('non-dynamic functions, cache function execution results')
            self.permanent_results = results_str

        return results_str

    def set_parameters(self, parameters: str):
        """设置函数入参
        """
        self.raw_parameters = parameters
        if not parameters:
            return

        from sendanywhere.engine.util import FunctionParser
        self.compiled_components = FunctionParser.compile_str(parameters)

        if len(self.compiled_components) > 1 or not isinstance(self.compiled_components[0], str):
            log.debug('function in compiled string')
            self.has_function = True

        self.permanent_results = None  # 在首次执行时进行计算和缓存

        for item in self.compiled_components:
            if isinstance(item, Function) or isinstance(item, SimpleVariable):
                log.debug('set as dynamic function')
                self.is_dynamic = True
                break

    @classmethod
    def get_named_function(cls, func_name):
        """根据函数名称获取函数对象
        """
        if func_name in cls.functions:
            return cls.functions[func_name]()
        else:
            return SimpleVariable(func_name)

    @classmethod
    def __init_functions__(cls):
        if not cls.functions:
            classes = ClassFinder.find_subclasses(Function)
            for clazz in classes.values():
                reference_key = clazz.REF_KEY
                if reference_key:
                    cls.functions[reference_key] = clazz
