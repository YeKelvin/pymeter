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

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.request_data = self.script
        result.sample_start()

        try:
            local_vars = {
                'log': log,
                'ctx': self.context,
                'vars': self.context.variables,
                'props': GlobalUtils.get_properties(),
                'prev': self.context.previous_result,
                'result': result,
                'success': result.success,
                'res': result.request_data,
            }
            exec(self.script, {}, local_vars)
        except Exception:
            result.success = False
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()
            result.calculate_elapsed_time()

        return result
