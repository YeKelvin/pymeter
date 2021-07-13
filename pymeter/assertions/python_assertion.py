#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_assertion.py.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
import traceback
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

    def get_result(self, result: SampleResult) -> AssertionResult:
        try:
            ctx = ContextService.get_context()
            props = GlobalUtils.get_properties()
            local_vars = {
                'log': log,
                'ctx': ctx,
                'vars': ctx.variables,
                'props': props,
                'prev': ctx.previous_result,
                'result': result,
                'failure': False,
                'failure_msg': ''
            }
            # setStopThread(boolean)
            # setStopTest(boolean)
            exec(self.script, {}, local_vars)
        except Exception:
            log.error(traceback.format_exc())
