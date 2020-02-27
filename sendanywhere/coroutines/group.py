#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group.py
# @Time    : 2020/2/13 12:58
# @Author  : Kelvin.Ye
from gevent import Greenlet

from sendanywhere.coroutines.context import CoroutineContext, ContextService
from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class CoroutineGroup(TestElement):
    # Sampler失败时的处理动作
    # 枚举：continue | start_next_loop | stop_coroutine | stop_test
    ON_SAMPLE_ERROR = 'CoroutineGroup.on_sample_error'

    ON_SAMPLE_ERROR_CONTINUE = 'continue'
    ON_SAMPLE_ERROR_START_NEXT_LOOP = 'start_next_loop'
    ON_SAMPLE_ERROR_STOP_COROUTINE = 'stop_coroutine'
    ON_SAMPLE_ERROR_STOP_TEST = 'stop_test'

    # 是否无限循环
    CONTINUE_FOREVER = 'CoroutineGroup.continue_forever'

    # 循环次数
    LOOPS = 'CoroutineGroup.loops'

    # 线程数
    NUMBER_COROUTINES = 'CoroutineGroup.number_coroutines'

    # 启用线程的间隔时间，单位 s
    START_INTERVAL = 'CoroutineGroup.start_interval'

    WAIT_TO_DIE = 5 * 1000

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
        self.group_tree = None
        self.all_coroutines: {Coroutine, Greenlet} = {}

    def start(self, group_number, group_tree, engine):
        self.running = True
        self.group_number = group_number
        self.group_tree = group_tree
        number_coroutines = self.number_coroutines
        context = ContextService.get_context()

        for coroutine_number in range(number_coroutines):
            if self.running:
                self.start_new_coroutine(group_tree, coroutine_number, engine, context)
            else:
                break

        log.info(f'Started thread group number {self.group_number}')

    def start_new_coroutine(self, group_tree, coroutine_number, engine, context):
        coroutine = self.make_coroutine(group_tree, coroutine_number, engine, context)
        greenlet = Greenlet(coroutine.run)
        greenlet.run()
        return coroutine

    def make_coroutine(self, group_tree, coroutine_number, engine, context):
        coroutine_name = f'{self.name} {self.group_number}-{coroutine_number + 1}'
        coroutine = Coroutine(group_tree, self, coroutine_number, coroutine_name, self.on_sample_error, engine)
        coroutine.initial_context(context)
        return coroutine

    def register_started_coroutine(self, coroutine, greenlet):
        self.all_coroutines[coroutine] = greenlet

    def wait_coroutines_stopped(self):
        for coroutine, greenlet in self.all_coroutines.items():
            self.__wait_coroutine_stopped(greenlet)

    def __wait_coroutine_stopped(self, greenlet: Greenlet):
        if not greenlet.dead():
            greenlet.join(self.WAIT_TO_DIE)


class Coroutine(Greenlet):
    LAST_SAMPLE_OK = 'Coroutine.last_sample_ok'

    def __init__(self,
                 group_tree: HashTree,
                 coroutine_group: CoroutineGroup,
                 coroutine_number: int,
                 coroutine_name: str,
                 on_sample_error: str,
                 engine,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.group_tree = group_tree
        self.coroutine_group = coroutine_group
        self.coroutine_number = coroutine_number
        self.coroutine_name = coroutine_name
        self.on_sample_error = on_sample_error
        self.engine = engine
        self.local_vars = {}
        self.running = True

    def initial_context(self, context: CoroutineContext):
        self.local_vars.update(context.variables)

    def run(self):
        context = ContextService.get_context()
        try:
            self.init_run(context)

        except Exception:
            pass

    def process_sampler(self):
        pass

    def init_run(self, context: CoroutineContext):
        context.variables = self.local_vars
        context.coroutine_number = self.coroutine_number
        context.variables[self.LAST_SAMPLE_OK] = 'true'
        context.coroutine = self
        context.coroutine_group = self.coroutine_group
        context.engine = self.engine
