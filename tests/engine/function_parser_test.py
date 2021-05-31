#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function_parser_test.py
# @Time    : 2021/5/30 17:23
# @Author  : Kelvin.Ye
from pymeter.engine.value_parser import FunctionParser


class FunctionParserTest:

    def test_compile_str(self):
        parser = FunctionParser()
        source = '{"keyAA":"valueAA","keyBB":"${__random(1, 10)}"}'
        result = parser.compile_str(source)
        print(result)
        print(type(result))


if __name__ == '__main__':
    ...
