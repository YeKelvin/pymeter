#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : context
# @Time    : 2019/3/15 9:39
# @Author  : Kelvin.Ye
from sendanywhere.threads.variables import SenderVariables
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SenderContext:
    def __init__(self):
        self.variables = SenderVariables()
        self.global_variables = None
        self.previous_result = None
        self.current_sampler = None
        self.previous_sampler = None
        self.engine = None
        self.thread = None
        self.threadGroup = None
        self.samplerContext = None


class SenderContextService:
    def __init__(self):
        self.context = None
        self.TestStartTime = None

    def start_test(self):
        pass

    def end_test(self):
        pass
