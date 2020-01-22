#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : replacer_test
# @Time    : 2020/1/19 10:31
# @Author  : Kelvin.Ye
from sendanywhere.engine.util import ValueReplacer


class TestValueReplacer:
    def test_replace_values(self):
        variables = {'varKey': 'actual value'}
        source = '{"keyA":"valueA","keyB":"${varKey}"}'
        replacer = ValueReplacer(variables)
        result = replacer.replace_values(source)
        print(result)
        assert '{"keyA":"valueA","keyB":"actual value"}' == result

    def test_replace_values_multiple(self):
        variables = {'varKey11': 'actual value11', 'varKey22': 'actual value22', 'varKey33': 'actual value33'}
        source = '{"keyA":"${varKey22}","keyB":"${varKey11}","keyC":"valueC","keyD":"${varKey33}"}'
        replacer = ValueReplacer(variables)
        result = replacer.replace_values(source)
        print(result)
        assert '{"keyA":"actual value22","keyB":"actual value11","keyC":"valueC","keyD":"actual value33"}' == result

    def test_replace_functions(self):
        variables = {}
        source = '{"keyAA":"valueAA","keyBB":"${__random(1, 10)}"}'
        replacer = ValueReplacer(variables)
        result = replacer.replace_functions(source)
        print(result)
