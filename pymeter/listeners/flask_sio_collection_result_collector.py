#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_sio_collection_result_collector.py.py
# @Time    : 2021/10/15 16:44
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
from pymeter.utils.time_util import timestamp_now
from pymeter.utils.time_util import timestamp_to_strftime


log = get_logger(__name__)


class FlaskSIOCollectionResultCollector(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
):

    # 消息接收方的 sid
    SID: Final = 'FlaskSIOCollectionResultCollector__sid'

    @property
    def sid(self):
        return self.get_property_as_str(self.SID)

    @property
    def collection(self):
        return ContextService.get_context().engine.collection

    @property
    def collection_id(self):
        return id(self.collection)

    @property
    def group(self):
        return ContextService.get_context().group

    @property
    def group_id(self):
        return id(self.group)

    def __init__(self):
        TestElement.__init__(self)

        self.flask_sio = None
        self.flask_sio_instance_module = 'app.extension'
        self.flask_sio_instance_name = 'socketio'

        self.namespace = '/'
        self.result_summary_event = 'pymeter_result_summary'
        self.result_event = 'pymeter_result'

        self.collection_start_time = 0
        self.collection_end_time = 0

    def init_flask_sio(self):
        module = importlib.import_module(self.flask_sio_instance_module)
        self.flask_sio = getattr(module, self.flask_sio_instance_name)

    def emit(self, name, data):
        self.flask_sio.emit(name, data, namespace=self.namespace, to=self.sid)

    def collection_started(self) -> None:
        """@override"""
        self.collection_start_time = timestamp_now()
        self.init_flask_sio()
        self.emit(self.result_summary_event, {
            'resultId': self.collection_id,
            'summary': {
                'resultName': self.collection.name,
                'resultType': 'COLLECTION',
                'startTime': timestamp_to_strftime(self.collection_start_time),
                'endTime': 0,
                'elapsedTime': 0,
                'running': True,
                'success': True
            },
            'result': []
        })

    def collection_ended(self) -> None:
        """@override"""
        self.collection_end_time = timestamp_now()
        self.emit(self.result_summary_event, {
            'resultId': self.collection_id,
            'summary': {
                'endTime': timestamp_to_strftime(self.collection_end_time),
                'elapsedTime': int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000),
                'running': False
            }
        })
        self.flask_sio.emit('pymeter_completed', namespace=self.namespace, to=self.sid)

    def group_started(self) -> None:
        """@override"""
        self.group.start_time = timestamp_now()
        self.emit(self.result_event, {
            'resultId': self.collection_id,
            'result': {
                'group': {
                    'groupId': self.group_id,
                    'groupName': self.group.name,
                    'startTime': time_util.strftime_now(),
                    'endTime': 0,
                    'elapsedTime': 0,
                    'running': True,
                    'success': True,
                    'children': []
                }
            }
        })

    def group_finished(self) -> None:
        """@override"""
        self.group.end_time = timestamp_now()
        self.emit(self.result_event, {
            'resultId': self.collection_id,
            'result': {
                'group': {
                    'groupId': self.group_id,
                    'endTime': time_util.strftime_now(),
                    'elapsedTime': int(self.group.end_time * 1000) - int(self.group.start_time * 1000),
                    'running': False
                }
            }
        })

    def sample_occurred(self, result) -> None:
        """@override"""
        if not result:
            return

        self.emit(self.result_event, {
            'resultId': self.collection_id,
            'result': {
                'group': {
                    'groupId': self.group_id,
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
                        'children': [sub.serialization for sub in result.sub_results]
                    }
                }
            }
        })

        if not result.success:
            self.emit(self.result_event, {
                'groupId': self.group_id,
                'group': {
                    'success': False
                }
            })

    def sample_started(self, sample) -> None:
        """@override"""
        ...

    def sample_ended(self, result) -> None:
        """@override"""
        ...

    def test_iteration_start(self, controller, iter) -> None:
        ...
