#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sql_sampler.py
# @Time    : 2020/2/17 15:33
# @Author  : Kelvin.Ye
from typing import Final

from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger


log = get_logger(__name__)


class SQLSampler(Sampler, TestElement):
    expression: Final = 'SQLSampler__expression'

    def sample(self) -> SampleResult:
        pass
