#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sql_sampler.py
# @Time    : 2020/2/17 15:33
# @Author  : Kelvin.Ye
from typing import Final

from tasker.elements.element import TaskElement
from tasker.samplers.sample_result import SampleResult
from tasker.samplers.sampler import Sampler
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class SQLSampler(Sampler, TaskElement):
    expression: Final = 'SQLSampler__expression'

    def sample(self) -> SampleResult:
        pass
