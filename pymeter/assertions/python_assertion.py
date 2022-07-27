#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_assertion.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.assertions.assertion import Assertion
from pymeter.assertions.assertion import AssertionResult
from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult
from pymeter.tools.python_code_snippets import DEFAULT_IMPORT_MODULE
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
        script = DEFAULT_IMPORT_MODULE + script

        ctx = ContextService.get_context()
        props = ctx.properties

        # 定义脚本中可用的内置变量
        params = {
            'log': log,
            'ctx': ctx,
            'vars': ctx.variables,
            'props': props,
            'prev': ctx.previous_result,
            'sampler': ctx.current_sampler,
            'result': response,
            'failure': not response.success,
            'message': None,
            'stop_group': response.stop_group,
            'stop_test': response.stop_test,
            'stop_test_now': response.stop_test_now
        }
        try:
            # 执行脚本（在模块层级上，globals 和 locals 是同一个字典）
            exec(script, params, params)
        except AssertionError as e:
            # 断言失败时，判断是否有定义失败信息，没有则返回断言脚本内容
            error_msg = str(e)
            if error_msg:
                raise
            else:
                raise AssertionError(self.script)

        # 更新断言结果
        result.failure = params['failure']
        result.message = params['message']

        # 更新 SamplerResult
        response.stop_group = params['stop_group']
        response.stop_test = params['stop_test']
        response.stop_test_now = params['stop_test_now']

        return result
