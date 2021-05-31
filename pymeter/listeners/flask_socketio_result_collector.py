#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_socket_result_collector.py
# @Time    : 2021/3/13 23:14
# @Author  : Kelvin.Ye
import importlib
from typing import Final

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


class FlaskSocketIOResultCollector(
    TestElement,
    TestCollectionListener,
    TestGroupListener,
    SampleListener,
    TestIterationListener,
    NoCoroutineClone
):

    # 命名空间
    NAMESPACE = 'FlaskSocketIOResultCollector__namespace'  # type: Final

    # 事件名称
    EVENT_NAME = 'FlaskSocketIOResultCollector__event_name'  # type: Final

    # 发送消息目标的sid
    TARGET_SID = 'FlaskSocketIOResultCollector__target_sid'  # type: Final

    # Flask-SocketIO实例所在的模块路径
    FLASK_SIO_INSTANCE_MODULE = 'FlaskSocketIOResultCollector__flask_sio_instance_module'  # type: Final

    # Flask-SocketIO实例的名称
    FLASK_SIO_INSTANCE_NAME = 'FlaskSocketIOResultCollector__flask_sio_instance_name'  # type: Final

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
    def __group_id(self) -> str:
        coroutine_group = ContextService.get_context().coroutine_group
        return f'{coroutine_group.name}-{coroutine_group.group_number}'

    @property
    def __group_name(self):
        return ContextService.get_context().coroutine_group.name

    def __init__(self):
        TestElement.__init__(self)

        self.reportName = None
        self.startTime = 0
        self.endTime = 0
        self.flask_sio = None

    def __set_flask_sio(self) -> type:
        module = importlib.import_module(self.flask_sio_instance_module)
        self.flask_sio = getattr(module, self.flask_sio_instance_name)

    def __emit_to_target(self, data):
        self.flask_sio.emit(self.event_name, data, namespace=self.namespace, to=self.target_sid)

    def collection_started(self) -> None:
        self.startTime = time_util.timestamp_as_ms()
        self.__set_flask_sio()

    def collection_ended(self) -> None:
        self.endTime = time_util.timestamp_as_ms()
        self.flask_sio.emit('disconnect', namespace=self.namespace, to=self.target_sid)

    def group_started(self) -> None:
        group_id = self.__group_id
        start_time = time_util.timestamp_as_ms()
        group_name = self.__group_name

        self.__emit_to_target({
            'group': {
                'groupId': group_id,
                'groupName': group_name,
                'startTime': start_time,
                'endTime': 0,
                'elapsedTime': 0,
                'success': True,
                'samplers': []
            }
        })

    def group_finished(self) -> None:
        group_id = self.__group_id
        end_time = time_util.timestamp_as_ms()

        self.__emit_to_target({'group': {'groupId': group_id, 'endTime': end_time, 'elapsedTime': 0}})

    def sample_started(self, sample) -> None:
        pass

    def sample_ended(self, sample_result) -> None:
        if not sample_result:
            return

        group_id = self.__group_id

        self.__emit_to_target({
            'sampler': {
                'groupId': group_id,
                'samplerName': sample_result.sample_label,
                'startTime': sample_result.start_time,
                'endTime': sample_result.end_time,
                'elapsedTime': sample_result.elapsed_time,
                'request': sample_result.request_body,
                'response': sample_result.response_data,
                'success': sample_result.success,
            }
        })

        if not sample_result.success:
            self.__emit_to_target({'group': {'groupId': group_id, 'success': False}})

    def test_iteration_start(self, controller) -> None:
        pass
