#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_path_assertion.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
from decimal import Decimal
from typing import Final

from pymeter.assertions.assertion import Assertion
from pymeter.assertions.assertion import AssertionResult
from pymeter.elements.element import TestElement
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.json_util import JsonpathExtractException
from pymeter.utils.json_util import json_path
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


JUDGMENT_TYPES = {
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

    # JsonPath 表达式
    JSONPATH: Final = 'JsonPathAssertion__jsonpath'

    # 期望值
    EXPECTED_VALUE: Final = 'JsonPathAssertion__expected_value'

    # 判断类型
    # 等于(EQUAL)、不等于(NOT_EQUAL)、大于(GREATER_THAN)、小于(LESS_THAN)
    # 包含(IN)、不包含(NOT_IN)
    # 开头包含(START_WITH)、结尾包含(END_WITH)
    # 存在(EXISTS)、不存在(NOT_EXISTS)
    # 正则匹配(REGULAR)
    JUDGMENT_TYPE: Final = 'JsonPathAssertion__judgment_type'

    @property
    def jsonpath(self):
        return self.get_property_as_str(self.JSONPATH)

    @property
    def expected_value(self):
        return self.get_property_as_str(self.EXPECTED_VALUE)

    @property
    def judgment_type(self):
        return self.get_property_as_str(self.JUDGMENT_TYPE)

    def get_result(self, sampler_result: SampleResult) -> AssertionResult:
        result = AssertionResult(self.name)
        response_data = sampler_result.response_data

        if not response_data:
            result.failure = True
            result.message = '响应结果为空'
            return result

        # JsonPath表达式
        jsonpath = self.jsonpath
        # 期望值
        expected_value = self.expected_value
        # 判断类型
        judgment_type = self.judgment_type
        
        if not jsonpath:
            result.failure = True
            result.message = 'JsonPath表达式为空，请修改后重试'
            return result
        
        if not judgment_type:
            result.failure = True
            result.message = '判断类型为空，请修改后重试'
            return result
    
        if judgment_type not in ['EXISTS', 'NOT_EXISTS'] and not expected_value:
            result.failure = True
            result.message = '期望值为空，请修改后重试'
            return result

        # 获取JsonPath实际值
        actual_value = None
        exists = True
        try:
            actual_value = json_path(response_data, jsonpath, throw=True)
        except JsonpathExtractException:
            exists = False

        # 等于
        if judgment_type == 'EQUAL' and str(actual_value) != expected_value:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 不等于
        if judgment_type == 'NOT_EQUAL' and str(actual_value) == expected_value:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 大于
        if judgment_type == 'GREATER_THAN' and not (Decimal(str(actual_value)) > Decimal(expected_value)):
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 小于
        if judgment_type == 'LESS_THAN' and not (Decimal(str(actual_value)) < Decimal(expected_value)):
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 包含
        if judgment_type == 'IN' and expected_value not in str(actual_value):
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 不包含
        if judgment_type == 'NOT_IN' and expected_value in str(actual_value):
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 开头包含
        if judgment_type == 'START_WITH' and not (str(actual_value).startswith(expected_value)):
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 结尾包含
        if judgment_type == 'END_WITH' and not (str(actual_value).endswith(expected_value)):
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 为null
        if judgment_type == 'NULL' and actual_value is not None:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 不为null
        if judgment_type == 'NOT_NULL' and actual_value is None:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 为空
        if judgment_type == 'BLANK' and not actual_value:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 不为空
        if judgment_type == 'NOT_BLANK' and actual_value:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 存在
        if judgment_type == 'EXISTS' and not exists:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 不存在
        if judgment_type == 'NOT_EXISTS' and exists:
            result.failure = True
            result.message = self.get_failure_message(actual_value)
            return result

        # 正则匹配
        if judgment_type == 'REGULAR':
            ...

        return result

    def get_failure_message(self, actual_value):
        return (
            'Json断言失败\n'
            f'元素名称: {self.name}\n'
            f'JsonPath表达式: {self.jsonpath}\n'
            f'JsonPath实际值: {actual_value}\n'
            f'判断类型: {JUDGMENT_TYPES.get(self.judgment_type)}\n'
            f'期望值: {self.expected_value}'
        )
