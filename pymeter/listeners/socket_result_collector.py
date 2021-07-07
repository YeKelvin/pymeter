#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socket_result_collector.py
# @Time    : 2021/2/9 11:48
# @Author  : Kelvin.Ye
import logging
from typing import Final

import socketio

from pymeter.elements.element import TestElement
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.groups.context import ContextService
from pymeter.groups.interface import NoCoroutineClone
from pymeter.utils import time_util
from pymeter.utils.json_util import from_json
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class SocketResultCollector(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
):
    # 连接地址
    URL: Final = 'SocketResultCollector__url'

    # 头部dict
    HEADERS: Final = 'SocketResultCollector__headers'

    # 命名空间
    NAMESPACE: Final = 'SocketResultCollector__namespace'

    # 事件名称
    EVENT_NAME: Final = 'SocketResultCollector__event_name'

    # 发送消息目标的sid
    TARGET_SID: Final = 'SocketResultCollector__target_sid'

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
    def group_id(self) -> str:
        return id(ContextService.get_context().coroutine_group)

    @property
    def group_name(self):
        return ContextService.get_context().coroutine_group.name

    def __init__(self):
        TestElement.__init__(self)

        self.reportName = None
        self.startTime = 0
        self.endTime = 0
        debug = True if log.level <= logging.DEBUG else False
        self.sio = socketio.Client(logger=debug, engineio_logger=debug)

    def __socket_connect(self):
        """连接socket.io"""
        namespace = '/'
        headers = {}

        if self.namespace:
            namespace = self.namespace
        if self.headers:
            headers = from_json(self.headers)

        log.info(f'socket start to connect url:[ {self.url} ] namespaces:[ {namespace} ]')
        self.sio.connect(self.url, headers=headers, namespaces=namespace)
        log.info(f'socket state:[ {self.sio.eio.state} ] sid:[ {self.sio.sid} ]')

    def __socket_disconnect(self):
        """关闭socket.io"""
        log.info('sid:[ {self.sio.sid} ] socket start to disconnect')
        if self.sio.connected:
            # 通知前端已执行完成
            self.sio.emit('execution_completed', {'to': self.target_sid})
            self.sio.emit('disconnect')

        self.sio.disconnect()

    def __emit_to_target(self, data: dict):
        """发送消息，data自动添加转发目标的sid"""
        data['to'] = self.target_sid
        self.sio.emit(self.event_name, data)

    def collection_started(self) -> None:
        self.startTime = time_util.timestamp_now()
        self.__socket_connect()

    def collection_ended(self) -> None:
        self.endTime = time_util.timestamp_now()
        self.__socket_disconnect()

    def group_started(self) -> None:
        self.__emit_to_target({
            'group': {
                'groupId': self.group_id,
                'groupName': self.group_name,
                'startTime': time_util.strftime_now(),
                'endTime': 0,
                'elapsedTime': 0,
                'running': True,
                'success': True,
                'samplers': []
            }
        })

    def group_finished(self) -> None:
        self.__emit_to_target({
            'groupId': self.group_id,
            'group': {
                'endTime': time_util.strftime_now(),
                'elapsedTime': 0,
                'running': False
            }
        })

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        if not sample_result:
            return

        group_id = self.__group_id

        group_id = self.group_id

        self.__emit_to_target({
            'groupId': group_id,
            'sampler': {
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
            }
        })

        if not sample_result.success:
            self.__emit_to_target({'groupId': group_id, 'group': {'success': False}})

    def test_iteration_start(self, controller) -> None:
        pass
