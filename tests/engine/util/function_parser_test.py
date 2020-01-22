#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function_parser_test
# @Time    : 2020/1/21 16:39
# @Author  : Kelvin.Ye
from sendanywhere.engine.util import FunctionParser


class TestFunctionParser:
    def test_compile_str(self):
        parser = FunctionParser()
        source = '{"keyAA":"valueAA","keyBB":"${__random(1, 10)}"}'
        result = parser.compile_str(source)
        print(result)
        print(type(result))
