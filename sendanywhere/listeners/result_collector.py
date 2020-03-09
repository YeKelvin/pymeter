#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : result_collector.py
# @Time    : 2020/2/18 17:20
# @Author  : Kelvin.Ye
from sendanywhere.coroutines.context import ContextService
from sendanywhere.engine.interface import (TestStateListener, CoroutineGroupListener, SampleListener,
                                           TestIterationListener, NoCoroutineClone)
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
        self.start_time = 0
        self.end_time = 0
        self.groups = {}

    def test_started(self) -> None:
        self.start_time = time_util.timestamp_as_ms()

    def test_ended(self) -> None:
        self.end_time = time_util.timestamp_as_ms()

    def group_started(self) -> None:
        coroutine_group = ContextService.get_context().coroutine_group
        group_id = coroutine_group.name + coroutine_group.group_number
        self.groups[group_id] = {
            'start_time': time_util.timestamp_as_ms(),
            'end_time': 0,
            'success': True,
            'group_name': ContextService.get_context().coroutine_name,
            'samplers': []
        }

    def group_finished(self) -> None:
        coroutine_group = ContextService.get_context().coroutine_group
        group_id = coroutine_group.name + coroutine_group.group_number
        self.groups[group_id]['end_time'] = time_util.timestamp_as_ms()

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        coroutine_group = ContextService.get_context().coroutine_group
        group_id = coroutine_group.name + coroutine_group.group_number
        self.groups[group_id]['samplers'].append({
            'start_time': sample_result.start_time,
            'end_time': sample_result.end_time,
            'elapsed_time': sample_result.elapsed_time,
            'success': sample_result.success,
            'sampler_name': sample_result.sample_label,
            'request': sample_result.request_body,
            'response': sample_result.response_data
        })

        if not sample_result.success:
            self.groups[group_id]['success'] = False

    def test_iteration_start(self, controller) -> None:
        pass
