#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group.py
# @Time    : 2020/2/13 12:58
# @Author  : Kelvin.Ye
import traceback
from enum import Enum, unique
from typing import Union

from gevent import Greenlet

from sendanywhere.controls.controller import Controller
from sendanywhere.controls.loop_controller import LoopController
from sendanywhere.coroutines.context import CoroutineContext, ContextService
from sendanywhere.engine.collection.traverser import TestCompiler
from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.engine.exceptions import StopTestException, StopTestNowException, StopCoroutineException
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


@unique
class LogicalAction(Enum):
    CONTINUE = 'continue'
    START_NEXT_LOOP = 'start_next_loop'
    STOP_COROUTINE = 'stop_coroutine'
    STOP_TEST = 'stop_test'
    STOPTEST_NOW = "stop_test_now"


class CoroutineGroup(LoopController):
    # Sampler失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR = 'CoroutineGroup.on_sample_error'

    # 线程数
    NUMBER_COROUTINES = 'CoroutineGroup.number_coroutines'

    # 启用线程的间隔时间，单位 s
    START_INTERVAL = 'CoroutineGroup.start_interval'

    # 默认等待协程结束时间，单位 ms
    WAIT_TO_DIE = 5 * 1000

    @property
    def on_sample_error(self):
        return self.get_property_as_str(self.ON_SAMPLE_ERROR)

    @property
    def on_error_stop_test(self):
        return self.on_sample_error == LogicalAction.STOP_TEST.value

    @property
    def on_error_stop_test_now(self):
        return self.on_sample_error == LogicalAction.STOPTEST_NOW.value

    @property
    def on_error_stop_coroutine(self):
        return self.on_sample_error == LogicalAction.STOP_COROUTINE.value

    @property
    def on_error_start_next_loop(self):
        return self.on_sample_error == LogicalAction.START_NEXT_LOOP.value

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

        log.info(f'Started coroutine group number [{self.group_number}]')

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
        self.test_compiler: Union[TestCompiler, None] = None

    def initial_context(self, context: CoroutineContext):
        self.local_vars.update(context.variables)

    def run(self):
        context = ContextService.get_context()
        try:
            self.init_run(context)
            while self.running:
                sample = self.coroutine_group.next()
                log.info(f'sample={sample}')
                # if sample is None:
                #     break
                while self.running and sample is not None:
                    #     self.process_sampler(sample, context)
                    last_sample_ok = context.variables.get(self.LAST_SAMPLE_OK)

                if self.coroutine_group.is_done():
                    self.running = False
                    log.info(f'Coroutine is done: {self.coroutine_name}')

        except Exception:
            log.error(traceback.format_exc())

    def process_sampler(self, current: Sampler, context: CoroutineContext):
        try:
            if current:
                self.execute_sample_package(current, context)

        except StopTestException:
            log.error(traceback.format_exc())
        except StopTestNowException:
            log.error(traceback.format_exc())
        except StopCoroutineException:
            log.error(traceback.format_exc())
        except Exception:
            log.error(traceback.format_exc())

    def execute_sample_package(self, current: Sampler, context: CoroutineContext):
        context.set_current_sampler(current)
        package = self.test_compiler.get_sample_package(current)

        # 执行 SampleListener.sample_started()

        # 执行前置处理器
        self.run_pre_processors(package.pre_processors)

        # 执行时间控制器 todo 后续补充时间控制器
        # self.delay(pack.timers)

        result = None
        if self.running:
            result = self.do_sampling(current, context)

        if result:
            context.set_current_sampler(result)

            # 执行后置处理器
            self.run_post_processors(package.post_processors)

            # 执行断言
            self.check_assertions(package.assertions, result, context)

            # 执行 SampleListener.sample_stopped()

            # 检查是否应停止线程或测试
            if result.is_stop_coroutine or (not result.is_successful and self.coroutine_group.on_error_stop_coroutine):
                self.stop_coroutine()
            if result.is_stop_test() or (not result.is_successful and self.coroutine_group.on_error_stop_test):
                self.shutdown_test()
            if result.is_stop_test_now() or (not result.is_successful and self.coroutine_group.on_error_stop_test_now):
                self.stop_test_now()

    def run_pre_processors(self, pre_processors: list):
        pass

    def do_sampling(self, sampler: Sampler, context: CoroutineContext) -> SampleResult:
        pass

    def run_post_processors(self, post_processors: list):
        pass

    def check_assertions(self, assertions: list, result: SampleResult, context: CoroutineContext):
        pass

    def stop_coroutine(self):
        self.running = False
        log.info(f'Stop Coroutine detected by coroutine: {self.coroutine_name}')

    def shutdown_test(self):
        pass

    def stop_test_now(self):
        self.running = False
        log.info(f'Stop Test Now detected by coroutine: {self.coroutine_name}')
        if self.engine:
            self.engine.stop_test()

    def init_run(self, context: CoroutineContext):
        context.variables = self.local_vars
        context.coroutine_number = self.coroutine_number
        context.variables[self.LAST_SAMPLE_OK] = 'true'
        context.coroutine = self
        context.coroutine_group = self.coroutine_group
        context.engine = self.engine

        # 储存 CoroutineGroup层的非 Sampler节点和非 Controller节点
        group_level_elements = self.group_tree.index(0).list()
        self.__remove_samplers_and_controllers(group_level_elements)

        # 编译 Group层下的所有子代节点
        self.test_compiler = TestCompiler(group_level_elements)
        self.group_tree.traverse(self.test_compiler)

    @staticmethod
    def __remove_samplers_and_controllers(elements: list):
        for element in elements[:]:
            if (
                    isinstance(element, Sampler) or
                    isinstance(element, Controller) or
                    not isinstance(element, TestElement)
            ):
                elements.remove(element)
