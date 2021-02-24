#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socket_result_collector.py
# @Time    : 2021/2/9 11:48
# @Author  : Kelvin.Ye
from typing import Final

from sendanywhere.coroutines.context import ContextService
from sendanywhere.engine.interface import (CoroutineGroupListener,
                                           NoCoroutineClone, SampleListener,
                                           TestIterationListener,
                                           TestStateListener)
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import time_util
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SocketResultCollector(TestElement,
                            TestStateListener,
                            CoroutineGroupListener,
                            SampleListener,
                            TestIterationListener,
                            NoCoroutineClone):
    EVENT_NAME = 'SocketResultCollector__event_name'  # type: Final

    @property
    def event_name(self):
        return self.get_property_as_str(self.EVENT_NAME)

    @property
    def __group_id(self) -> str:
        coroutine_group = ContextService.get_context().coroutine_group
        return f'{coroutine_group.name}-{coroutine_group.group_number}'

    @property
    def __group_name(self):
        return ContextService.get_context().coroutine_group.name

    def __init__(self, name: str = None, comments: str = None):
        super().__init__(name, comments)
        self.reportName = None
        self.startTime = 0
        self.endTime = 0
        self.groups = {}

    def test_started(self) -> None:
        self.startTime = time_util.timestamp_as_ms()

    def test_ended(self) -> None:
        self.endTime = time_util.timestamp_as_ms()

    def group_started(self) -> None:
        self.groups[self.__group_id] = {
            'startTime': time_util.timestamp_as_ms(),
            'endTime': 0,
            'success': True,
            'groupName': self.__group_name,
            'samplers': []
        }

    def group_finished(self) -> None:
        self.groups[self.__group_id]['endTime'] = time_util.timestamp_as_ms()

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        if sample_result:
            self.groups[self.__group_id]['samplers'].append({
                'startTime': sample_result.start_time,
                'endTime': sample_result.end_time,
                'elapsedTime': sample_result.elapsed_time,
                'success': sample_result.success,
                'samplerName': sample_result.sample_label,
                'request': sample_result.request_body,
                'response': sample_result.response_data
            })

            if not sample_result.success:
                self.groups[self.__group_id]['success'] = False

    def test_iteration_start(self, controller) -> None:
        pass
