#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function_parser
# @Time    : 2020/1/19 16:17
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger
from sendanywhere.utils.str_reader import StringReader

log = get_logger(__name__)


class FunctionParser:

    def compile_str(self, source: str):
        result = []
        buffer = []
        previous = ''
        reader = StringReader(source)
        while True:
            current = reader.next
            if current is None:  # 遍历完成跳出循环
                break
            if current == '\\':  # 匹配 "\" 转义符
                previous = current
                current = reader.next
                if current is None:  # 遍历完成跳出循环
                    break
                # Keep '\' unless it is one of the escapable chars '$' ',' or '\'
                #  N.B. This method is used to parse function parameters, so must treat ',' as special
                if current != '$' and current != ',' and current[0] != '\\':
                    buffer.append(previous)
                previous = ''
                buffer.append(current)
            elif current == '{' and previous == '$':  # 匹配 "${" 占位符前缀
                buffer = buffer[:-1]
                if len(buffer) > 0:  # save leading text
                    result.append(''.join(buffer))
                    buffer = []
                result.append(self._make_function(reader))
                previous = ''
            else:
                buffer.append(current)
                previous = current

        if len(buffer) > 0:
            result.append(''.join(buffer))

        return ''.join(result)

    def _make_function(self, reader: StringReader):
        buffer = []
        previous = ''
        while True:
            current = reader.next
            if current is None:  # 遍历完成跳出循环
                break
            if current == '\\':
                current = reader.next
                if current is None:  # 遍历完成跳出循环
                    break
                previous = ''
                buffer.append(current)
            elif current == '(' and previous != '':
                funcName = ''.join(buffer)
                parameters = self._parse_params(reader)

    def _parse_params(self, reader: StringReader):
        buffer = []
        previous = ''
        while True:
            current = reader.next
            if current is None:  # 遍历完成跳出循环
                break
            if current == '\\':
                buffer.append(current)  # Store the \
                current = reader.next
                if current is None:  # 遍历完成跳出循环
                    break
                previous = ''
                buffer.append(current)
            elif current == ',':
