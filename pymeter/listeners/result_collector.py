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

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        if not sample_result:
            return

        self.groups[self.group_id]['samplers'].append({
            'samplerId': id(sample_result),
            'samplerName': sample_result.sample_name,
            'samplerRemark': sample_result.sample_remark,
            'url': sample_result.request_url,
            'request': sample_result.request_data,
            'requestHeaders': sample_result.request_headers,
            'response': sample_result.response_data,
            'responseHeaders': sample_result.response_headers,
            'responseCode': sample_result.response_code,
            'responseMessage': sample_result.response_message,
            'requestSize': sample_result.request_size,
            'responseSize': sample_result.response_size,
            'success': sample_result.success,
            'startTime': time_util.timestamp_to_strftime(sample_result.start_time),
            'endTime': time_util.timestamp_to_strftime(sample_result.end_time),
            'elapsedTime': sample_result.elapsed_time,
        })

        if not sample_result.success:
            self.groups[self.group_id]['success'] = False

    def test_iteration_start(self, controller) -> None:
        pass
