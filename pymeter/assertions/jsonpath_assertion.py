#!/usr/bin python3
# @File    : jsonpath_assertion.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
from decimal import Decimal
from typing import Final

from orjson import JSONDecodeError

from pymeter.assertions.assertion import Assertion
from pymeter.assertions.assertion import AssertionResult
from pymeter.elements.element import TestElement
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.json_util import JsonpathExtractException
from pymeter.utils.json_util import json_path


OPERATORS = {
    'EQUAL': '等于',
    'NOT_EQUAL': '不等于',
    'GREATER_THAN': '大于',
    'LESS_THAN': '小于',
    'IN': '包含',
    'NOT_IN': '不包含',
    'START_WITH': '开头包含',
    'END_WITH': '结尾包含',
    'NULL': '为null',
    'NOT_NULL': '不为null',
    'BLANK': '为空',
    'NOT_BLANK': '不为空',
    'EXISTS': '存在',
    'NOT_EXISTS': '不存在',
    'REGULAR': '正则匹配',
}


class JsonPathAssertion(Assertion, TestElement):

    # 表达式
    JSONPATH: Final = 'JsonPathAssertion__jsonpath'

    # 操作符
    OPERATOR: Final = 'JsonPathAssertion__operator'

    # 期望值
    EXPECTED_VALUE: Final = 'JsonPathAssertion__expected_value'

    @property
    def jsonpath(self):
        return self.get_property_as_str(self.JSONPATH)

    @property
    def operator(self):
        return self.get_property_as_str(self.OPERATOR)

    @property
    def expected_value(self):
        return self.get_property_as_str(self.EXPECTED_VALUE)

    def get_result(self, sampler_result: SampleResult) -> AssertionResult:
        result = AssertionResult(self.name)
        response_data = sampler_result.response_data

        if not response_data:
            return self.fail(result, msg='响应结果为空')

        # JsonPath表达式
        jsonpath = self.jsonpath
        # 判断类型
        operator = self.operator
        # 期望值
        expected_value = self.expected_value

        if not jsonpath:
            return self.fail(result, msg='JsonPath不允许为空')

        if not operator:
            return self.fail(result, msg='判断类型不允许为空')

        if operator not in ['NULL', 'NOT_NULL', 'BLANK', 'NOT_BLANK', 'EXISTS', 'NOT_EXISTS'] and not expected_value:
            return self.fail(result, msg='期望值不允许为空')

        # 获取JsonPath实际值
        actual_value = None
        exists = True
        try:
            actual_value = json_path(response_data, jsonpath, throw=True)
        except (JsonpathExtractException, JSONDecodeError):
            exists = False

        # 等于
        if operator == 'EQUAL' and str(actual_value) != expected_value:
            return self.fail(result, actual_value, exists)

        # 不等于
        if operator == 'NOT_EQUAL' and str(actual_value) == expected_value:
            return self.fail(result, actual_value, exists)

        # 大于
        if operator == 'GREATER_THAN' and not (Decimal(str(actual_value)) > Decimal(expected_value)):
            return self.fail(result, actual_value, exists)

        # 小于
        if operator == 'LESS_THAN' and not (Decimal(str(actual_value)) < Decimal(expected_value)):
            return self.fail(result, actual_value, exists)

        # 包含
        if operator == 'IN' and expected_value not in str(actual_value):
            return self.fail(result, actual_value, exists)

        # 不包含
        if operator == 'NOT_IN' and expected_value in str(actual_value):
            return self.fail(result, actual_value, exists)

        # 开头包含
        if operator == 'START_WITH' and not (str(actual_value).startswith(expected_value)):
            return self.fail(result, actual_value, exists)

        # 结尾包含
        if operator == 'END_WITH' and not (str(actual_value).endswith(expected_value)):
            return self.fail(result, actual_value, exists)

        # 为null
        if operator == 'NULL' and actual_value is not None:
            return self.fail(result, actual_value, exists)

        # 不为null
        if operator == 'NOT_NULL' and actual_value is None:
            return self.fail(result, actual_value, exists)

        # 为空
        if operator == 'BLANK' and actual_value:
            return self.fail(result, actual_value, exists)

        # 不为空
        if operator == 'NOT_BLANK' and not actual_value:
            return self.fail(result, actual_value, exists)

        # 存在
        if operator == 'EXISTS' and not exists:
            return self.fail(result, actual_value, exists)

        # 不存在
        if operator == 'NOT_EXISTS' and exists:
            return self.fail(result, actual_value, exists)

        # 正则匹配
        if operator == 'REGULAR':
            ...

        return result

    def fail(self, result: AssertionResult, actual_value=None, exists=None, msg=None):
        result.failure = True
        result.message = msg or self.get_failure_message(actual_value, exists)
        return result

    def get_failure_message(self, actual_value, exists):
        if exists:
            actual_value = actual_value if actual_value is not None else "null"
        else:
            actual_value = None

        return (
            f'元素名称: {self.name}\n'
            f'断言结果: 失败\n'
            f'判断类型: {OPERATORS.get(self.operator)}\n'
            f'表达式: {self.jsonpath}\n'
            f'期望值: {self.get_expectation()}\n'
            f'实际值: {actual_value}'
        )

    def get_expectation(self):
        operator = self.operator

        if operator == 'NULL':
            return '为空(null)'
        elif operator == 'NOT_NULL':
            return '非空(not null)'
        elif operator == 'BLANK':
            return '为空(blank)'
        elif operator == 'NOT_BLANK':
            return '非空(not blank)'
        elif operator == 'EXISTS':
            return '存在'
        elif operator == 'EXNOT_EXISTSISTS':
            return '不存在'
        else:
            return self.expected_value
