#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.engine.globalization import GlobalUtils
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
            res = self.wrapper(
                log=log,
                ctx=self.context,
                vars=self.context.variables,
                props=GlobalUtils.get_properties(),
                prev=self.context.previous_result,
                result=result
            )
            if res:
                result.response_data = res
        except Exception:
            result.success = False
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()
            result.calculate_elapsed_time()

        return result
