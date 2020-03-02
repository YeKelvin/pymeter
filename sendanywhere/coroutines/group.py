#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group.py
# @Time    : 2020/2/13 12:58
# @Author  : Kelvin.Ye
import traceback
from enum import Enum, unique
from typing import Union

from gevent import Greenlet

from sendanywhere.assertions.assertion import AssertionResult
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
class TestLogicalAction(Enum):
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
    def on_error_continue(self):
        return self.on_sample_error == TestLogicalAction.CONTINUE.value

    @property
    def on_error_start_next_loop(self):
        return self.on_sample_error == TestLogicalAction.START_NEXT_LOOP.value

    @property
    def on_error_stop_coroutine(self):
        return self.on_sample_error == TestLogicalAction.STOP_COROUTINE.value

    @property
    def on_error_stop_test(self):
        return self.on_sample_error == TestLogicalAction.STOP_TEST.value

    @property
    def on_error_stop_test_now(self):
        return self.on_sample_error == TestLogicalAction.STOPTEST_NOW.value

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

        log.info(f'已经开始第 [{self.group_number}] 个协程组')

    def start_new_coroutine(self, group_tree, coroutine_number, engine, context):
        """以一个协程执行协程组
        """
        coroutine = self.make_coroutine(group_tree, coroutine_number, engine, context)
        greenlet = Greenlet(coroutine.run)
        greenlet.run()
        return coroutine

    def make_coroutine(self, group_tree, coroutine_number, engine, context):
        """创建一个协程
        """
        coroutine_name = f'{self.name} {self.group_number}-{coroutine_number + 1}'
        coroutine = Coroutine(group_tree, self, coroutine_number, coroutine_name, engine)
        coroutine.initial_context(context)
        coroutine.on_error_continue = self.on_error_continue
        coroutine.on_error_stop_test = self.on_error_stop_test
        coroutine.on_error_stop_test_now = self.on_error_stop_test_now
        coroutine.on_error_stop_coroutine = self.on_error_stop_coroutine
        coroutine.on_error_start_next_loop = self.on_error_start_next_loop
        return coroutine

    def register_started_coroutine(self, coroutine, greenlet):
        """存储所有的协程和 Greenlet对象，用于停止协程
        """
        self.all_coroutines[coroutine] = greenlet

    def wait_coroutines_stopped(self):
        """等待所有协程停止
        """
        for coroutine, greenlet in self.all_coroutines.items():
            self.__wait_coroutine_stopped(greenlet)

    def __wait_coroutine_stopped(self, greenlet: Greenlet):
        """等待协程停止
        """
        if not greenlet.dead():
            greenlet.join(self.WAIT_TO_DIE)

    def stop(self) -> None:
        """停止所有协程
        """
        self.running = False
        for coroutine in self.all_coroutines.keys():
            coroutine.stop()

    def tell_coroutines_to_stop(self) -> None:
        """杀死所有协程
        """
        self.running = False
        for coroutine, greenlet in self.all_coroutines.items():
            coroutine.stop()
            # coroutine.interrupt()  # todo 实现中断
            greenlet.kill()


class Coroutine(Greenlet):
    LAST_SAMPLE_OK = 'Coroutine.last_sample_ok'

    def __init__(self,
                 group_tree: HashTree,
                 coroutine_group: CoroutineGroup,
                 coroutine_number: int,
                 coroutine_name: str,
                 engine,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.group_tree = group_tree
        self.coroutine_group = coroutine_group
        self.coroutine_number = coroutine_number
        self.coroutine_name = coroutine_name
        self.on_error_continue = False
        self.on_error_stop_test = False
        self.on_error_stop_test_now = False
        self.on_error_stop_coroutine = False
        self.on_error_start_next_loop = False
        self.engine = engine
        self.local_vars = {}
        self.test_compiler: Union[TestCompiler, None] = None
        self.start_time = 0
        self.end_time = 0

        # todo SearchByClass(TestIterationListener)

    def initial_context(self, context: CoroutineContext):
        """将父协程（运行 StandardEngine的协程）的本地变量赋值给子协程的本地变量中
        """
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
                    self.process_sampler(sample, context)
                    last_sample_ok = context.variables.get(self.LAST_SAMPLE_OK)

                    if not self.on_error_continue or (self.on_error_start_next_loop and not last_sample_ok):
                        log.debug(
                            'Start Next Continue Loop option is on, Last sample failed, starting next continue loop'
                        )

                        if self.on_error_start_next_loop and not last_sample_ok:
                            pass
                        else:
                            pass
                    else:
                        sample = self.coroutine_group.next()

                if self.coroutine_group.is_done:
                    self.running = False
                    log.info(f'Coroutine is done: {self.coroutine_name}')

        except Exception:
            log.error(traceback.format_exc())

    def continue_on_coroutine_loop(self):
        pass

    def continue_on_current_loop(self):
        pass

    def break_on_current_loop(self):
        pass

    def process_sampler(self, current: Sampler, context: CoroutineContext):
        """
        执行取样器
        这里主要是捕获异常，以控制是否需要停止测试
        """
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
        """根据取样器的子代执行取样器
        """
        context.set_current_sampler(current)
        package = self.test_compiler.get_sample_package(current)

        # 执行 SampleListener.sample_started()

        # 执行前置处理器
        self.run_pre_processors(package.pre_processors)

        # 执行时间控制器 todo 后续补充时间控制器
        # self.delay(pack.timers)

        # 执行取样器
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
            if result.is_stop_coroutine or (not result.is_successful and self.on_error_stop_coroutine):
                self.stop_coroutine()
            if result.is_stop_test or (not result.is_successful and self.on_error_stop_test):
                self.shutdown_test()
            if result.is_stop_test_now or (not result.is_successful and self.on_error_stop_test_now):
                self.stop_test_now()

    def do_sampling(self, sampler: Sampler, context: CoroutineContext) -> SampleResult:
        """执行取样器
        """
        sampler.context = context
        sampler.coroutine_name = self.coroutine_name
        return sampler.sample()

    def check_assertions(self, assertions: list, result: SampleResult, context: CoroutineContext) -> None:
        """断言取样器结果
        """
        for assertion in assertions:
            self.process_assertion(assertion, result)

        context.variables[self.LAST_SAMPLE_OK] = result.is_successful

    @staticmethod
    def process_assertion(assertion, result: SampleResult):
        """执行断言
        """
        try:
            assertion_result = assertion.get_result(result)
        except AssertionError as e:
            log.debug(f'Error processing Assertion: {e}')
            assertion_result = AssertionResult()
            assertion_result.is_failure = True
            assertion_result.failure_message = str(e)
        except RuntimeError as e:
            log.error(f'Error processing Assertion: {e}')
            assertion_result = AssertionResult()
            assertion_result.is_error = True
            assertion_result.failure_message = str(e)
        except Exception as e:
            log.error(f'Exception processing Assertion: {e}')
            log.error(traceback.format_exc())
            assertion_result = AssertionResult()
            assertion_result.is_error = True
            assertion_result.failure_message = str(e)

        result.is_successful(result.is_successful and not (assertion_result.is_Error or assertion_result.is_failure))
        result.assertion_result = assertion_result

    def stop_coroutine(self):
        """停止协程
        """
        self.running = False
        log.info(f'Stop Coroutine detected by coroutine: {self.coroutine_name}')

    def shutdown_test(self):
        self.running = False
        log.info(f'Shutdown Test detected by coroutine: {self.coroutine_name}')
        if self.engine:
            self.engine.ask_coroutines_to_stop()

    def stop_test_now(self):
        self.running = False
        log.info(f'Stop Test Now detected by coroutine: {self.coroutine_name}')
        if self.engine:
            self.engine.stop_test()

    def init_run(self, context: CoroutineContext):
        """
        协程执行前的初始化动作，包括以下动作：
        1、给 CoroutineContext赋值
        2、将 group层的非 Sampler节点和非 Controller节点传递给子代
        3、编译子代节点
        """
        context.variables = self.local_vars
        context.coroutine_number = self.coroutine_number
        context.variables[self.LAST_SAMPLE_OK] = 'true'
        context.coroutine = self
        context.coroutine_group = self.coroutine_group
        context.engine = self.engine

        # 储存 group层的非 Sampler节点和非 Controller节点
        group_level_elements = self.group_tree.index(0).list()
        self.__remove_samplers_and_controllers(group_level_elements)

        # 编译 Group层下的所有子代节点
        self.test_compiler = TestCompiler(group_level_elements)
        self.group_tree.traverse(self.test_compiler)

    def stop(self):
        self.running = False
        log.info(f'Stopping: {self.coroutine_name}')

    @staticmethod
    def run_pre_processors(pre_processors: list) -> None:
        """执行前置处理器
        """
        for pre_processor in pre_processors:
            log.debug(f'Running preprocessor: {pre_processor.name}')
            pre_processor.process()

    @staticmethod
    def run_post_processors(post_processors: list):
        """执行后置处理器
        """
        for post_processor in post_processors:
            log.debug(f'Running postprocessor: {post_processor.name}')
            post_processor.process()

    @staticmethod
    def __remove_samplers_and_controllers(elements: list):
        """删除 Sampler和 Controller节点
        """
        for element in elements[:]:
            if (
                    isinstance(element, Sampler) or
                    isinstance(element, Controller) or
                    not isinstance(element, TestElement)
            ):
                elements.remove(element)
