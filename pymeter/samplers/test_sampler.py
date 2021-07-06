#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_sampler
# @Time    : 2020/3/3 17:58
# @Author  : Kelvin.Ye
from typing import Final

import gevent

from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TestSampler(Sampler):

    DATA: Final = 'TestSampler__data'

    SUCCESS: Final = 'TestSampler__success'

    @property
    def data(self):
        return self.get_property_as_str(self.DATA)

    @property
    def success(self):
        return self.get_property_as_bool(self.SUCCESS)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.name
        result.request_data = self.data
        result.sample_start()
        gevent.sleep(0.5)
        result.sample_end()
        result.success = self.success
        result.response_data = self.data
        result.calculate_elapsed_time()

        return result
