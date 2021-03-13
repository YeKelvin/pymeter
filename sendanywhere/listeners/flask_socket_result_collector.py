#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_socket_result_collector.py
# @Time    : 2021/3/13 23:14
# @Author  : Kelvin.Ye
from flask_socketio import emit
from sendanywhere.coroutines.context import ContextService
from sendanywhere.engine.interface import (CoroutineGroupListener,
                                           NoCoroutineClone, SampleListener,
                                           TestIterationListener,
                                           TestStateListener)
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import time_util
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class FlaskSocketResultCollector(TestElement,
                                 TestStateListener,
                                 CoroutineGroupListener,
                                 SampleListener,
                                 TestIterationListener,
                                 NoCoroutineClone):
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

    def test_started(self) -> None:
        self.startTime = time_util.timestamp_as_ms()
        self.__socket_connect()

    def test_ended(self) -> None:
        self.endTime = time_util.timestamp_as_ms()
        self.__socket_disconnect()

    def group_started(self) -> None:
        group_id = self.__group_id
        start_time = time_util.timestamp_as_ms()
        group_name = self.__group_name

        emit({
            'group': {
                'id': group_id,
                'startTime': start_time,
                'endTime': 0,
                'success': True,
                'groupName': group_name,
                'samplers': []
            }
        })

    def group_finished(self) -> None:
        group_id = self.__group_id
        end_time = time_util.timestamp_as_ms()

        emit({
            'group': {
                'id': group_id,
                'endTime': end_time
            }
        })

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        if not sample_result:
            return

        group_id = self.__group_id

        emit({
            'sampler': {
                'groupId': group_id,
                'startTime': sample_result.start_time,
                'endTime': sample_result.end_time,
                'elapsedTime': sample_result.elapsed_time,
                'success': sample_result.success,
                'samplerName': sample_result.sample_label,
                'request': sample_result.request_body,
                'response': sample_result.response_data
            }
        })

        if not sample_result.success:
            emit({
                'group': {
                    'id': group_id,
                    'success': False
                }
            })

    def test_iteration_start(self, controller) -> None:
        pass
