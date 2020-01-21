#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function_parser
# @Time    : 2020/1/19 16:17
# @Author  : Kelvin.Ye
from sendanywhere.engine.exceptions import InvalidVariableException
from sendanywhere.engine.util import CompoundVariable
from sendanywhere.functions import Function
from sendanywhere.utils.log_util import get_logger
from sendanywhere.utils.str_reader import StringReader

log = get_logger(__name__)


class FunctionParser:

    def compile_str(self, source: str) -> []:
        reader = StringReader(source)
        result = []
        buffer = []
        previous = ''
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
                buffer = buffer[:-1]
                if len(buffer) > 0:  # 保存 "${" 占位符前的字符串
                    before_placeholder_str = ''.join(buffer)
                    log.debug(f'匹配到 "${{}}" 占位符，报错占位符前的字符串:[ {before_placeholder_str} ]')
                    result.append(before_placeholder_str)
                    buffer.clear()
                    log.debug('清空 buffer')
                result.append(self._make_function(reader))
                previous = ''
            else:
                buffer.append(current)
                previous = current

        if len(buffer) > 0:
            result.append(''.join(buffer))

        if len(result) == 0:
            result.append('')

        return result

    def _make_function(self, reader: StringReader) -> Function or str:
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
                funcName = ''.join(buffer)
                log.debug(f'function name={funcName}')
                function = CompoundVariable.get_named_function(funcName)
                log.debug(f'function={function}')
                if isinstance(function, Function):
                    function.set_parameters(self._parse_params(reader))
                    current = reader.next
                    if current is None or current != '}':
                        raise InvalidVariableException(
                            f'Expected }} after {funcName} function call in {reader.raw}'
                        )
                    return function
                else:  # 函数不存在，按普通字符处理
                    buffer.append(current)
            elif current == '}':  # 变量 或者没有参数的函数
                function = CompoundVariable.get_named_function(''.join(buffer))
                log.debug(f'function={function}')
                if isinstance(function, Function):  # 确保调用 set_parameters()
                    function.set_parameters([])
                buffer.clear()
                log.debug('清空 buffer')
                return function
            else:
                buffer.append(current)
                previous = current

        str_buffer = ''.join(buffer)
        log.warn(f'可能是无效的函数字符串:[ {str_buffer} ]')
        return str_buffer

    def _parse_params(self, reader: StringReader) -> [CompoundVariable]:
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
                log.debug(f'param str={param_str}')
                param = CompoundVariable(param_str)
                buffer.clear()
                log.debug('清空 buffer')
                result.append(param)
            elif current == ')' and function_recursion == 0 and parent_recursion == 0:
                # 检测function name，防止生成空字符串作为参数
                if len(buffer) == 0 and len(result) == 0:
                    return result
                # 正常退出
                param_str = ''.join(buffer)
                log.debug(f'param str={param_str}')
                param = CompoundVariable(param_str)
                buffer.clear()
                log.debug('清空 buffer')
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

        # 退出，未匹配到参数列表结束符 "）"
        str_buffer = ''.join(buffer)
        log.warn(f'可能是无效的函数字符串:[ {str_buffer} ]')
        var = CompoundVariable()
        var.set_parameters(str_buffer)
        result.append(var)
        return result
