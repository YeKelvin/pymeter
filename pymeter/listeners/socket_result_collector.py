#!/usr/bin python3
# @File    : socket_result_collector.py
# @Time    : 2021/2/9 11:48
# @Author  : Kelvin.Ye
import logging
from typing import Final

import socketio
from loguru import logger

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoThreadClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.groups.context import ContextService
from pymeter.utils import time_util
from pymeter.utils.json_util import from_json


class SocketResultCollector(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoThreadClone
):
    # 连接地址
    URL: Final = 'SocketResultCollector__url'

    # 请求头
    HEADERS: Final = 'SocketResultCollector__headers'

    # 命名空间
    NAMESPACE: Final = 'SocketResultCollector__namespace'

    # 事件名称
    EVENT_NAME: Final = 'SocketResultCollector__event_name'

    # 发送消息目标的 sid
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
        return id(ContextService.get_context().group)

    @property
    def group_name(self):
        return ContextService.get_context().group.name

    def __init__(self):
        TestElement.__init__(self)

        self.reportName = None
        self.startTime = 0
        self.endTime = 0
        debug = logger.level <= logging.DEBUG
        self.sio = socketio.Client(logger=debug, engineio_logger=debug)

    def __socket_connect(self):
        """连接 socket.io"""
        namespace = self.namespace or '/'
        headers = from_json(self.headers) if self.headers else {}

        logger.info(f'socket start to connect url:[ {self.url} ] namespaces:[ {namespace} ]')
        self.sio.connect(self.url, headers=headers, namespaces=namespace)
        logger.info(f'socket state:[ {self.sio.eio.state} ] sid:[ {self.sio.sid} ]')

    def __socket_disconnect(self):
        """关闭 socket.io"""
        logger.info('sid:[ {self.sio.sid} ] socket start to disconnect')
        if self.sio.connected:
            # 通知前端已执行完成
            self.sio.emit('execution_completed', {'to': self.target_sid})
            self.sio.emit('disconnect')

        self.sio.disconnect()

    def __emit_to_target(self, data: dict):
        """发送消息，data 自动添加转发目标的 sid"""
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

    def sample_occurred(self, result) -> None:
        if not result:
            return

        group_id = self.__group_id

        group_id = self.group_id

        self.__emit_to_target({
            'groupId': group_id,
            'sampler': {
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
                'assertions': [str(assertion) for assertion in result.assertions],
                'subResults': [sub.serialization for sub in result.sub_results]
            }
        })

        if not result.success:
            self.__emit_to_target({'groupId': group_id, 'group': {'success': False}})

    def sample_started(self, sample) -> None:
        ...

    def sample_ended(self, result) -> None:
        ...

    def test_iteration_start(self, controller, iter) -> None:
        ...
