#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.engine.globalization import GlobalUtils
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
    def script_wrapper(self):
        func = ['def func(log, ctx, vars, props, prev, result):\n']

        if not self.script or self.script.isspace():
            func.append('\t...\n')
        else:
            lines = self.script.split('\n')
            for line in lines:
                func.append(f'\t{line}\n')

        func.append('self.wrapper = func')
        return ''.join(func)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.request_data = self.script
        result.sample_start()

        try:
            exec(self.script_wrapper, {}, {'self': self})
            ctx = ContextService.get_context()
            props = GlobalUtils.get_properties()
            res = self.wrapper(
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
