#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from sendanywhere.engine.globalization import GlobalUtils
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class PythonSampler(Sampler, TestElement):
    SOURCE: Final = 'PythonSampler__source'

    @property
    def source(self):
        return self.get_property_as_str(self.SOURCE)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.name
        result.request_body = self.source
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
                'response_data': result.response_data
            }
            exec(self.source, {}, local_vars)
        except Exception:
            result.response_data = traceback.format_exc()

        result.sample_end()
        result.calculate_elapsed_time()

        return result
