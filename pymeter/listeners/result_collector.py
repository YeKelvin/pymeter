#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : result_collector.py
# @Time    : 2020/2/18 17:20
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.groups.context import ContextService
from pymeter.groups.interface import NoCoroutineClone
from pymeter.utils import time_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class ResultCollector(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
):

    def __init__(self):
        TestElement.__init__(self)
        self.reportName = None
        self.startTime = 0
        self.endTime = 0
        self.groups = {}

    @property
    def group_id(self) -> str:
        return id(ContextService.get_context().coroutine_group)

    @property
    def group_name(self):
        return ContextService.get_context().coroutine_group.name

    def collection_started(self) -> None:
        self.startTime = time_util.timestamp_now()

    def collection_ended(self) -> None:
        self.endTime = time_util.timestamp_now()

    def group_started(self) -> None:
        self.groups[self.group_id] = {
            'groupId': self.group_id,
            'groupName': self.group_name,
            'startTime': time_util.strftime_now(),
            'endTime': 0,
            'elapsedTime': 0,
            'success': True,
            'samplers': []
        }

    def group_finished(self) -> None:
        self.groups[self.group_id]['endTime'] = time_util.strftime_now()

    def sample_occurred(self, result) -> None:
        ...

    def sample_started(self, sample) -> None:
        ...

    def sample_ended(self, result) -> None:
        if not result:
            return

        self.groups[self.group_id]['samplers'].append({
            'samplerId': id(result),
            'samplerName': result.sample_name,
            'samplerRemark': result.sample_remark,
            'url': result.request_url,
            'request': result.request_data,
            'requestHeaders': result.request_headers,
            'response': result.response_data,
            'responseHeaders': result.response_headers,
            'responseCode': result.response_code,
            'responseMessage': result.response_message,
            'requestSize': result.request_size,
            'responseSize': result.response_size,
            'success': result.success,
            'startTime': time_util.timestamp_to_strftime(result.start_time),
            'endTime': time_util.timestamp_to_strftime(result.end_time),
            'elapsedTime': result.elapsed_time,
        })

        if not result.success:
            self.groups[self.group_id]['success'] = False

    def test_iteration_start(self, controller) -> None:
        ...
