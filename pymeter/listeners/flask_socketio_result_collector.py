#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_socket_result_collector.py
# @Time    : 2021/3/13 23:14
# @Author  : Kelvin.Ye
import importlib
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.groups.context import ContextService
from pymeter.utils import time_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class FlaskSocketIOResultCollector(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
):

    # 命名空间
    NAMESPACE: Final = 'FlaskSocketIOResultCollector__namespace'

    # 事件名称
    EVENT_NAME: Final = 'FlaskSocketIOResultCollector__event_name'

    # 发送消息目标的 sid
    TARGET_SID: Final = 'FlaskSocketIOResultCollector__target_sid'

    # Flask-SocketIO 实例所在的模块路径
    FLASK_SIO_INSTANCE_MODULE: Final = 'FlaskSocketIOResultCollector__flask_sio_instance_module'

    # Flask-SocketIO 实例的名称
    FLASK_SIO_INSTANCE_NAME: Final = 'FlaskSocketIOResultCollector__flask_sio_instance_name'

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
    def flask_sio_instance_module(self):
        return self.get_property_as_str(self.FLASK_SIO_INSTANCE_MODULE)

    @property
    def flask_sio_instance_name(self):
        return self.get_property_as_str(self.FLASK_SIO_INSTANCE_NAME)

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
        self.flask_sio = None

    def init_flask_sio(self) -> type:
        module = importlib.import_module(self.flask_sio_instance_module)
        self.flask_sio = getattr(module, self.flask_sio_instance_name)

    def emit_to_target(self, data):
        self.flask_sio.emit(self.event_name, data, namespace=self.namespace, to=self.target_sid)

    def collection_started(self) -> None:
        """@override"""
        self.startTime = time_util.timestamp_now()
        self.init_flask_sio()

    def collection_ended(self) -> None:
        """@override"""
        self.endTime = time_util.timestamp_now()
        self.flask_sio.emit('pymeter_completed', namespace=self.namespace, to=self.target_sid)

    def group_started(self) -> None:
        """@override"""
        self.emit_to_target({
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
        """@override"""
        self.emit_to_target({
            'groupId': self.group_id,
            'group': {
                'endTime': time_util.strftime_now(),
                'elapsedTime': 0,
                'running': False
            }
        })

    def sample_occurred(self, result) -> None:
        """@override"""
        if not result:
            return

        group_id = self.group_id

        self.emit_to_target({
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
                'subResults': [result.serialization for result in result.sub_results]
            }
        })

        if not result.success:
            self.emit_to_target({'groupId': group_id, 'group': {'success': False}})

    def sample_started(self, sample) -> None:
        """@override"""
        ...

    def sample_ended(self, result) -> None:
        """@override"""
        ...

    def test_iteration_start(self, controller, iter) -> None:
        ...
