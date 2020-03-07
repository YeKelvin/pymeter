#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
from sendanywhere.engine.globalization import GlobalUtils
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class PythonSampler(Sampler, TestElement):
    SOURCE = 'PythonSampler.source'

    @property
    def source(self):
        return self.get_property_as_str(self.SOURCE)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.name
        result.request_body = self.source
        result.sample_start()

        local_vars = {
            'log': log,
            'ctx': self.context,
            'vars': self.context.variables,
            'props': GlobalUtils.get_properties(),
            'prev': self.context.previous_result,
            'result': result,
            'is_successful': result.is_successful,
            'response_data': result.response_data
        }
        exec(self.source, {}, local_vars)

        result.sample_end()
        result.calculate_elapsed_time()

        return result


if __name__ == '__main__':
    code = '''
aa = 'bb'
log.info('11')
print(aa)
'''
    result = exec(code, {'log': log})
