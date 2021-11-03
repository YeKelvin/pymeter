#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.common.python_support import DEFAULT_LOCAL_IMPORT_MODULE
from pymeter.common.python_support import INDENT
from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonSampler(Sampler):

    # 脚本内容
    SCRIPT: Final = 'PythonSampler__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    @property
    def function_wrapper(self):
        func = ['def func(log, ctx, vars, props, prev, result):\n' + DEFAULT_LOCAL_IMPORT_MODULE]

        if not self.script or self.script.isspace():
            func.append(f'{INDENT}...\n')
        else:
            lines = self.script.split('\n')
            for line in lines:
                func.append(f'{INDENT}{line}\n')

        func.append('self.function = func')
        return ''.join(func)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.request_data = self.script
        result.sample_start()

        # noinspection PyBroadException
        try:
            # 定义脚本中可用的内置变量
            params = {'self': self}
            exec(self.function_wrapper, params, params)
            ctx = ContextService.get_context()
            props = ctx.properties
            res = self.function(
                log=log,
                ctx=ctx,
                vars=ctx.variables,
                props=props,
                prev=ctx.previous_result,
                result=result
            )
            if res:
                result.response_data = res
        except Exception:
            result.success = False
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()

        return result
