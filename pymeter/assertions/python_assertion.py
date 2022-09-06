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
from pymeter.tools.python_code_snippets import DEFAULT_LOCAL_IMPORT_MODULE
from pymeter.tools.python_code_snippets import INDENT
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonAssertion(Assertion):

    # 脚本内容
    SCRIPT: Final = 'PythonAssertion__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    @property
    def raw_function(self):
        func = [
            'def function(log, ctx, vars, props, prev, sampler, result):\n',
            DEFAULT_LOCAL_IMPORT_MODULE
        ]

        content = self.script
        if not content or content.isspace():  # 脚本内容为空则生成空函数
            func.append(f'{INDENT}...\n')
        else:
            lines = content.split('\n')
            func.extend(f'{INDENT}{line}\n' for line in lines)
        func.append('self.dynamic_function = function')
        return ''.join(func)

    def get_result(self, response: SampleResult) -> AssertionResult:
        result = AssertionResult(self.name)

        try:
            ctx = ContextService.get_context()
            props = ctx.properties
            params = {
                'self': self,
                'failure': not response.success,
                'message': None,
            }
            exec(self.raw_function, params, params)
            self.dynamic_function(  # noqa
                log=log,
                ctx=ctx,
                vars=ctx.variables,
                props=props,
                prev=ctx.previous_result,
                sampler=ctx.current_sampler,
                result=response
            )
        except AssertionError as e:
            # 断言失败时，判断是否有定义失败信息，没有则返回断言脚本内容
            error_msg = str(e)
            if error_msg:
                raise
            else:
                raise AssertionError(self.script) from e

        # 更新断言结果
        result.failure = params['failure']
        result.message = params['message']

        return result
