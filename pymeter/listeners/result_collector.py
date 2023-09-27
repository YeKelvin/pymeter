#!/usr/bin python3
# @File    : result_collector.py
# @Time    : 2020/2/18 17:20
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement
from pymeter.engines.interface import NoThreadClone
from pymeter.engines.interface import SampleListener
from pymeter.engines.interface import TestCollectionListener
from pymeter.engines.interface import TestIterationListener
from pymeter.engines.interface import TestWorkerListener
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.time_util import strftime_now
from pymeter.utils.time_util import timestamp_now
from pymeter.utils.time_util import timestamp_to_strftime
from pymeter.workers.context import ContextService


class ResultCollector(
    TestElement,
    TestCollectionListener,
    TestWorkerListener,
    TestIterationListener,
    SampleListener,
    NoThreadClone
):

    def __init__(self):
        TestElement.__init__(self)
        self.report_name = None
        self.start_time = 0
        self.end_time = 0
        self.workers = {}

    @property
    def worker_id(self) -> str:
        return id(ContextService.get_context().worker)

    @property
    def worker(self):
        return ContextService.get_context().worker

    def collection_started(self) -> None:
        self.start_time = timestamp_now()

    def collection_ended(self) -> None:
        self.end_time = timestamp_now()

    def worker_started(self) -> None:
        self.workers[self.worker_id] = {
            'workerId': self.worker_id,
            'workerName': self.worker.name,
            'startTime': strftime_now(),
            'endTime': 0,
            'elapsedTime': 0,
            'success': True,
            'samplers': []
        }

    def worker_finished(self) -> None:
        self.workers[self.worker_id]['endTime'] = strftime_now()

    def sample_occurred(self, result: SampleResult) -> None:
        if not result:
            return

        self.workers[self.worker_id]['samplers'].append({
            'samplerId': id(result),
            'samplerName': result.sample_name,
            'samplerDesc': result.sample_desc,
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
            'startTime': timestamp_to_strftime(result.start_time),
            'endTime': timestamp_to_strftime(result.end_time),
            'elapsedTime': result.elapsed_time,
            'assertions': [str(assertion) for assertion in result.assertions],
            'subResults': [sub.to_dict() for sub in result.subresults]
        })

        if not result.success:
            self.workers[self.worker_id]['success'] = False

    def sample_started(self, sample) -> None:
        ...

    def sample_ended(self, result) -> None:
        ...

    def test_iteration_start(self, controller, iter) -> None:
        ...
