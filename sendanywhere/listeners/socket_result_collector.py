#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socket_result_collector.py
# @Time    : 2021/2/9 11:48
# @Author  : Kelvin.Ye
from sendanywhere.coroutines.context import ContextService
from sendanywhere.engine.interface import (TestStateListener, CoroutineGroupListener, SampleListener, TestIterationListener, NoCoroutineClone)
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import time_util
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class ResultCollector(TestElement,
                      TestStateListener,
                      CoroutineGroupListener,
                      SampleListener,
                      TestIterationListener,
                      NoCoroutineClone):
    def __init__(self, name: str = None, comments: str = None):
        super().__init__(name, comments)
        self.reportName = None
        self.startTime = 0
        self.endTime = 0
        self.groups = {}
