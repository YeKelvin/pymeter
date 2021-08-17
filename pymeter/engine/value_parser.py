#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function_parser
# @Time    : 2021/5/30 17:11
# @Author  : Kelvin.Ye
from typing import List

from pymeter.common.exceptions import InvalidVariableException
from pymeter.elements.property import BasicProperty
from pymeter.elements.property import FunctionProperty
from pymeter.functions import Function
from pymeter.groups.context import ContextService
from pymeter.utils.class_finder import ClassFinder
from pymeter.utils.log_util import get_logger
from pymeter.utils.str_reader import StringReader


log = get_logger(__name__)


class CompoundVariable:
    """复合变量"""
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
        """执行函数"""
        if not self.is_dynamic and self.permanent_results:  # 优先返回函数执行结果缓存
            log.debug('return cache results')
            return self.permanent_results

        if not self.compiled_components:
            log.debug('compiled component is empty')
            return ''

        results = []
        for item in self.compiled_components:
            if isinstance(item, Function):
                log.debug(f'appending execution result from function:[ {item.REF_KEY} ]')
                results.append(item.execute())
            elif isinstance(item, SimpleVariable):
                log.debug(f'appending actual value from variable:[ {item.name} ]')
                results.append(item.value)
            else:
                results.append(item)
        results_str = ''.join(results)

        if not self.is_dynamic:
            log.debug('non-dynamic functions, cache function execution results')
            self.permanent_results = results_str

        return results_str

    def set_parameters(self, parameters: str):
        """设置函数入参"""
        self.raw_parameters = parameters
        if not parameters:
            return

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
        """根据函数名称获取函数对象"""
        if func_name in cls.functions:
            return cls.functions[func_name]()
        else:
            return SimpleVariable(func_name)

    @classmethod
    def __init_functions__(cls):
        if cls.functions:
            return

        classes = ClassFinder.find_subclasses(Function)
        for clazz in classes.values():
            reference_key = clazz.REF_KEY
            if reference_key:
                cls.functions[reference_key] = clazz


class SimpleVariable:

    def __init__(self, name: str = None):
        self.name = name

    @property
    def variables(self):
        return ContextService.get_context().variables

    @property
    def value(self):
        if self.name in self.variables:
            return self.variables.get(self.name)
        else:
            return '${' + self.name + '}'


class FunctionParser:

    @staticmethod
    def compile_str(source: str) -> List:
        reader = StringReader(source)
        result = []
        buffer = []
        previous = ''
        log.debug(f'start compiling string, source: {source}')
        while True:
            current = reader.next
            if current is None:  # end of reader
                log.debug('end of reader')
                break
            if current == '\\':  # 匹配 "\" 转义符
                previous = current
                current = reader.next
                if current is None:  # end of reader
                    log.debug('end of reader')
                    break
                # 保留 "\"，除非当前字符是 "$" 或 "\"
                # 注意：此方法用于解析函数参数，因此必须将 "，" 视为特殊的字符
                if current != '$' and current != ',' and current[0] != '\\':
                    buffer.append(previous)
                previous = ''
                buffer.append(current)
            elif current == '{' and previous == '$':  # 匹配 "${" 占位符前缀
                log.debug('found a "${"')
                buffer = buffer[:-1]
                if len(buffer) > 0:  # 保存 "${" 占位符前的字符串
                    before_placeholder_str = ''.join(buffer)
                    log.debug(f'save the string before the placeholder: {before_placeholder_str}')
                    result.append(before_placeholder_str)
                    buffer.clear()
                result.append(FunctionParser.__make_function(reader))
                previous = ''
            else:
                buffer.append(current)
                previous = current

        if len(buffer) > 0:
            result.append(''.join(buffer))

        if len(result) == 0:
            result.append('')

        return result

    @staticmethod
    def __make_function(reader: StringReader) -> Function or str:
        buffer = []
        previous = ''
        while True:
            current = reader.next
            if current is None:  # end of reader
                log.debug('end of reader')
                break
            if current == '\\':
                current = reader.next
                if current is None:  # end of reader
                    log.debug('end of reader')
                    break
                previous = ''
                buffer.append(current)
            elif current == '(' and previous != '':
                func_name = ''.join(buffer)
                log.debug(f'function reference key: {func_name}')
                function = CompoundVariable.get_named_function(func_name)
                if isinstance(function, Function):
                    function.set_parameters(FunctionParser.__parse_params(reader))
                    current = reader.next
                    if current is None or current != '}':
                        raise InvalidVariableException(f'expected }} after {func_name} function call in {reader.raw}')
                    return function
                else:  # 函数不存在，按普通字符处理
                    buffer.append(current)
            elif current == '}':  # 变量 或者没有参数的函数
                func_name = ''.join(buffer)
                log.debug(f'function reference key: {func_name}')
                function = CompoundVariable.get_named_function(func_name)
                if isinstance(function, Function):  # 确保调用 set_parameters()
                    function.set_parameters([])
                buffer.clear()
                return function
            else:
                buffer.append(current)
                previous = current

        str_buffer = ''.join(buffer)
        log.warn(f'may be invalid function string: {str_buffer}')
        return str_buffer

    @staticmethod
    def __parse_params(reader: StringReader) -> List[CompoundVariable]:
        result = []
        buffer = []
        previous = ''
        function_recursion = 0
        parent_recursion = 0
        while True:
            current = reader.next
            if current is None:  # end of reader
                log.debug('end of reader')
                break
            if current == '\\':
                buffer.append(current)  # Store the \
                current = reader.next
                if current is None:  # end of reader
                    log.debug('end of reader')
                    break
                previous = ''
                buffer.append(current)
            elif current == ',' and function_recursion == 0:
                param_str = ''.join(buffer)
                log.debug(f'parameter str: {param_str}')
                param = CompoundVariable(param_str)
                buffer.clear()
                result.append(param)
            elif current == ')' and function_recursion == 0 and parent_recursion == 0:
                # 检测 function name，防止生成空字符串作为参数
                if len(buffer) == 0 and len(result) == 0:
                    return result
                # 正常退出
                param_str = ''.join(buffer)
                log.debug(f'raw parameter: {param_str}')
                param = CompoundVariable(param_str)
                buffer.clear()
                result.append(param)
                return result
            elif current == '{' and previous == '$':
                buffer.append(current)
                previous = current
                function_recursion += function_recursion
            elif current == '}' and function_recursion > 0:
                buffer.append(current)
                previous = current
                function_recursion -= function_recursion
            elif current == ')' and function_recursion == 0 and parent_recursion > 0:
                buffer.append(current)
                previous = current
                parent_recursion -= parent_recursion
            elif current[0] == '(' and function_recursion == 0:
                buffer.append(current)
                previous = current[0]
                parent_recursion += parent_recursion
            else:
                buffer.append(current)
                previous = current

        # 退出，未匹配到参数列表结束符 ")"
        str_buffer = ''.join(buffer)
        log.warn(f'may be invalid function string: {str_buffer}')
        var = CompoundVariable()
        var.set_parameters(str_buffer)
        result.append(var)
        return result


class ValueReplacer:

    @staticmethod
    def replace_values(key: str, source: str) -> BasicProperty:
        master_function = CompoundVariable()
        master_function.set_parameters(source)
        if master_function.has_function:
            return FunctionProperty(key, master_function)
        return BasicProperty(key, source)
