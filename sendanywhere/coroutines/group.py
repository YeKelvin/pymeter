#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group.py
# @Time    : 2020/2/13 12:58
# @Author  : Kelvin.Ye
from gevent import Greenlet

from sendanywhere.coroutines.context import CoroutineContext
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class CoroutineGroup(TestElement):
    # Sampler失败时的处理动作
    # 枚举：continue | start_next_loop | stop_coroutine | stop_test
    ON_SAMPLE_ERROR = 'CoroutineGroup.on_sample_error'

    # 是否无限循环
    CONTINUE_FOREVER = 'CoroutineGroup.continue_forever'

    # 循环次数
    LOOPS = 'CoroutineGroup.loops'

    # 线程数
    NUMBER_COROUTINES = 'CoroutineGroup.number_coroutines'

    # 启用线程的间隔时间，单位 s
    START_INTERVAL = 'CoroutineGroup.start_interval'

    @property
    def on_sample_error(self):
        return self.get_property_as_str(self.ON_SAMPLE_ERROR)

    @property
    def continue_forever(self):
        return self.get_property_as_bool(self.CONTINUE_FOREVER)

    @property
    def loops(self):
        return self.get_property_as_int(self.LOOPS)

    @property
    def number_coroutines(self):
        return self.get_property_as_int(self.NUMBER_COROUTINES)

    @property
    def start_interval(self):
        return self.get_property_as_float(self.START_INTERVAL)

    def __init__(self, name: str = None, comments: str = None, propertys: dict = None):
        super().__init__(name, comments, propertys)
        self.running = False
        self.group_number = None

    def start(self, group_count: int, group_tree, engine):
        pass


class Coroutine(Greenlet):
    LAST_SAMPLE_OK = 'Coroutine.last_sample_ok'

    def __init__(self, tree, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vars = {}
        self.running = True

    def initial_context(self, context: CoroutineContext):
        self.vars.update(context.variables)

    def run(self):
        pass
