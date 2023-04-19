#!/usr/bin python3
# @File    : value_replacer_test.py
# @Time    : 2021/5/30 17:23
# @Author  : Kelvin.Ye
from pymeter.engine.values import ValueReplacer


class ValueReplacerTest:

    def test_replace_values_not_exist(self):
        source = '{"keyA":"valueA","keyB":"${varKey}"}'
        replacer = ValueReplacer()
        result = replacer.replace_values(source)
        print(result)
        assert '{"keyA":"valueA","keyB":"${varKey}"}' == result

    def test_replace_values_multiple(self):
        source = '{"keyA":"${varKey22}","keyB":"${varKey11}","keyC":"valueC","keyD":"${varKey33}"}'
        replacer = ValueReplacer()
        result = replacer.replace_values(source)
        print(result)
        assert '{"keyA":"actual value22","keyB":"actual value11","keyC":"valueC","keyD":"actual value33"}' == result

    def test_replace_functions(self):
        source = '{"keyAA":"valueAA","keyBB":"${__random(1, 10)}"}'
        replacer = ValueReplacer()
        result = replacer.replace_values(source)
        print(result)

    def test_replace_functions_multiple(self):
        source = (
            '{'
            '"keyAA":"valueAA",'
            '"keyBB":"${__Random(1, 10)}",'
            '"keyCC":"${__Time()}",'
            '"keyDD":"${__Time(%Y-%m-%d %H:%M:%S)}"}'
        )
        replacer = ValueReplacer()
        result = replacer.replace_values(source)
        print(result)


if __name__ == '__main__':
    ...
