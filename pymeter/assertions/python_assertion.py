#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_assertion.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.assertions.assertion import Assertion
from pymeter.assertions.assertion import AssertionResult
from pymeter.engine.globalization import GlobalUtils
from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonAssertion(Assertion):

    # 脚本内容
    SCRIPT: Final = 'PythonAssertion__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    def get_result(self, response: SampleResult) -> AssertionResult:
        result = AssertionResult(self.name)

        script = self.script
        if not script:
            return result

        ctx = ContextService.get_context()
        props = GlobalUtils.get_properties()

        # 定义局部变量
        local_vars = {
            'log': log,
            'ctx': ctx,
            'vars': ctx.variables,
            'props': props,
            'prev': ctx.previous_result,
            'result': response,
            'failure': not response.success,
            'message': None,
            'stop_group': response.stop_group,
            'stop_test': response.stop_test,
            'stop_test_now': response.stop_test_now
        }

        # 执行脚本
        exec(script, {}, local_vars)

        # 更新断言结果
        result.failure = local_vars['failure']
        result.message = local_vars['message']

        # 更新 SamplerResult
        response.stop_group = local_vars['stop_group']
        response.stop_test = local_vars['stop_test']
        response.stop_test_now = local_vars['stop_test_now']

        return result
