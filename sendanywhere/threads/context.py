#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : context
# @Time    : 2019/3/15 9:39
# @Author  : Kelvin.Ye
import time

from sendanywhere.engine.globalization import SenderUtils
from sendanywhere.threads.variables import SenderVariables
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SenderContext:
    def __init__(self):
        self.variables = SenderVariables()
        self.previous_result = None
        self.current_sampler = None
        self.previous_sampler = None
        self.sampling_started = False
        self.thread = None
        self.threadGroup = None
        self.samplerContext = None
        self.thread_num = None

    def set_current_sampler(self, sampler):
        self.previous_sampler = self.current_sampler
        self.current_sampler = sampler


class SenderContextService:
    contexts: {str, SenderContext} = {}
    test_start = 0
    number_of_active_threads = 0
    number_of_threads_started = 0
    number_of_threads_finished = 0
    total_threads = 0

    @classmethod
    def get_context(cls, id) -> SenderContext:
        return cls.contexts.get(id)

    @classmethod
    def remove_context(cls, id) -> None:
        del cls.contexts[id]

    @classmethod
    def replace_context(cls, id, context) -> None:
        cls.contexts[id] = context

    @classmethod
    def start_test(cls):
        if cls.test_start == 0:
            cls.numberOfActiveThreads = 0
            cls.test_start = int(time.time() * 1000)
            SenderUtils.set_property('TESTSTART.MS', cls.test_start)

    @classmethod
    def end_test(cls):
        cls.test_start = 0

    @classmethod
    def incr_number_of_threads(cls):
        """增加活动线程的数量
        """
        cls.number_of_active_threads += 1
        cls.number_of_threads_started += 1

    @classmethod
    def decr_number_of_threads(cls):
        """减少活动线程的数量
        """
        cls.number_of_active_threads -= 1
        cls.number_of_threads_finished += 1

    @classmethod
    def add_total_threads(cls, group_number: int):
        cls.total_threads += group_number

    @classmethod
    def clear_total_threads(cls):
        cls.total_threads = 0
        cls.number_of_threads_started = 0
        cls.number_of_threads_finished = 0
