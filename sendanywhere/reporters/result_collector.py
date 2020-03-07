#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : result_collector.py
# @Time    : 2020/2/18 17:20
# @Author  : Kelvin.Ye
from sendanywhere.engine.listener import TestStateListener, CoroutineGroupListener, SampleListener, \
    TestIterationListener
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class ResultCollector(TestStateListener,
                      CoroutineGroupListener,
                      SampleListener,
                      TestIterationListener):
    def test_started(self) -> None:
        pass

    def test_ended(self) -> None:
        pass

    def group_started(self) -> None:
        pass

    def group_finished(self) -> None:
        pass

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        pass

    def test_iteration_start(self, controller) -> None:
        pass
