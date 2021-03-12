#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socket_result_collector.py
# @Time    : 2021/2/9 11:48
# @Author  : Kelvin.Ye
from typing import Final

import socketio
from sendanywhere.coroutines.context import ContextService
from sendanywhere.engine.interface import (CoroutineGroupListener,
                                           NoCoroutineClone, SampleListener,
                                           TestIterationListener,
                                           TestStateListener)
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import time_util
from sendanywhere.utils.json_util import from_json
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SocketResultCollector(TestElement,
                            TestStateListener,
                            CoroutineGroupListener,
                            SampleListener,
                            TestIterationListener,
                            NoCoroutineClone):
    # 连接地址
    URL = 'SocketResultCollector__url'  # type: Final

    # 头部dict
    HEADERS = 'SocketResultCollector__headers'  # type: Final

    # 命名空间
    NAMESPACE = 'SocketResultCollector__namespace'  # type: Final

    # 事件名称
    EVENT_NAME = 'SocketResultCollector__event_name'  # type: Final

    # 发送消息目标的sid
    TARGET_SID = 'SocketResultCollector__target_sid'  # type: Final

    @property
    def url(self):
        return self.get_property_as_str(self.URL)

    @property
    def headers(self):
        return self.get_property_as_str(self.HEADERS)

    @property
    def namespace(self):
        return self.get_property_as_str(self.NAMESPACE)

    @property
    def event_name(self):
        return self.get_property_as_str(self.EVENT_NAME)

    @property
    def target_sid(self):
        return self.get_property_as_str(self.TARGET_SID)

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
        self.sio = socketio.AsyncClient()

    def __socket_connect(self):
        """连接socket.io"""
        namespace = None
        headers = {}

        if self.namespace:
            namespace = self.namespace
        if self.headers:
            headers = from_json(self.headers)

        log.debug(f'socket start to connect url:[ {self.url} ] namespaces:[ {namespace} ]')
        self.sio.connect(self.url, headers=headers, namespaces=namespace)

    def __socket_disconnect(self):
        """关闭socket.io"""
        log.debug('socket start to disconnect')
        if self.sio.connected:
            # 断开socket连接前先发送执行完成的事件
            self.sio.emit('execution_completed')
            self.sio.emit('disconnect')

        self.sio.close()

    def emit(self, data: dict):
        """发送消息，data自动添加转发目标的sid"""
        data['to'] = self.target_sid
        self.sio.emit(self.event_name, data)

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

        self.emit({
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

        self.emit({
            'group': {
                'id': group_id,
                'endTime': end_time
            }
        })

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        if sample_result:
            return

        group_id = self.__group_id

        self.emit({
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
            self.emit({
                'group': {
                    'id': group_id,
                    'success': False
                }
            })

    def test_iteration_start(self, controller) -> None:
        pass
