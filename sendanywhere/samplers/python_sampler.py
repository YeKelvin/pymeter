#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class PythonSampler(Sampler, TestElement):
    SOURCE = 'PythonSampler.source'

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.get_property_as_str(self.LABEL)
        result.request_body = self.get_property_as_str(self.SOURCE)
        result.sample_start()

        # - log：打印日志
        # - ctx：请求上下文对象
        # - vars(dict)：局部变量
        # - props(dict)：全局变量
        # - prev：上一个请求的请求对象
        # - sampler：当前请求的请求对象
        # - data(str)：当前请求的请求报文
        # - response(str)：当前请求的响应报文
        exec(self.get_property_as_str(self.SOURCE), {}, locals())

        result.sample_end()
        result.success = True
        result.response_data = ''
        result.elapsed_time = f'{result.end_time - result.start_time} ms'

        return result


if __name__ == '__main__':
    code = '''
aa = 'bb'
print(aa)
return 0
    '''
    result = exec(code)
    print(result)
