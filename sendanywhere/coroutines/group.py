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
from sendanywhere.coroutines.variables import Variables
from sendanywhere.engine.collection.traverser import TestCompiler, FindTestElementsUpToRoot, SearchByClass
from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.engine.exceptions import StopTestException, StopTestNowException, StopCoroutineException
from sendanywhere.engine.listener import IteratingController, TestIterationListener, CoroutineGroupListener, \
    LoopIterationListener
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


@unique
class TestLogicalAction(Enum):
    """取样器错误时，下一步动作的逻辑枚举
    """
    # 错误时继续
    CONTINUE = 'continue'

    # 错误时开始下一个协程控制器的循环
    START_NEXT_COROUTINE_LOOP = 'start_next_coroutine_loop'

    # 错误时开始下一个当前控制器（协程控制器或子代控制器）的循环
    START_NEXT_CURRENT_LOOP = 'start_next_current_loop'

    # 错误时中断当前控制器的循环
    BREAK_CURRENT_LOOP = 'break_current_loop'

    # 错误时停止协程
    STOP_COROUTINE = 'stop_coroutine'

    # 错误时停止测试执行
    STOP_TEST = 'stop_test'

    # 错误时立即停止测试执行（中断协程）
    STOPTEST_NOW = 'stop_test_now'


class CoroutineGroup(LoopController):
    # Sampler失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR = 'CoroutineGroup.on_sample_error'

    # 线程数
    NUMBER_COROUTINES = 'CoroutineGroup.number_coroutines'

    # 启用线程的间隔时间，单位 s todo 占坑，后面实现启动时间间隔
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
    def on_error_start_next_coroutine_loop(self):
        return self.on_sample_error == TestLogicalAction.START_NEXT_COROUTINE_LOOP.value

    @property
    def on_error_start_next_current_loop(self):
        return self.on_sample_error == TestLogicalAction.START_NEXT_CURRENT_LOOP.value

    @property
    def on_error_break_current_loop(self):
        return self.on_sample_error == TestLogicalAction.BREAK_CURRENT_LOOP.value

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
                self.__start_new_coroutine(group_tree, coroutine_number, engine, context)
            else:
                break

        log.info(f'已开始第 [{self.group_number}] 个协程组')

    def wait_coroutines_stopped(self):
        """等待所有协程停止
        """
        for coroutine, greenlet in self.all_coroutines.items():
            self.__wait_coroutine_stopped(greenlet)

    def stop_coroutines(self) -> None:
        """停止所有协程
        """
        self.running = False
        for coroutine in self.all_coroutines.keys():
            coroutine.stop_coroutine()

    def kill_coroutines(self) -> None:
        """杀死所有协程
        """
        self.running = False
        for coroutine, greenlet in self.all_coroutines.items():
            coroutine.stop()
            # coroutine.interrupt()  # todo 实现中断
            greenlet.kill()

    def __start_new_coroutine(self, group_tree, coroutine_number, engine, context):
        """以一个协程执行协程组
        """
        coroutine = self.__make_coroutine(group_tree, coroutine_number, engine, context)
        greenlet = Greenlet(coroutine.run)
        self.__register_started_coroutine(coroutine, greenlet)
        greenlet.run()
        return coroutine

    def __make_coroutine(self, group_tree, coroutine_number, engine, context):
        """创建一个协程
        """
        coroutine_name = f'{self.name} {self.group_number}-{coroutine_number + 1}'
        coroutine = Coroutine(group_tree, self, coroutine_number, coroutine_name, engine)
        coroutine.initial_context(context)
        coroutine.on_error_continue = self.on_error_continue
        coroutine.on_error_start_next_coroutine_loop = self.on_error_start_next_coroutine_loop
        coroutine.on_error_start_next_current_loop = self.on_error_start_next_current_loop
        coroutine.on_error_break_current_loop = self.on_error_break_current_loop
        coroutine.on_error_stop_coroutine = self.on_error_stop_coroutine
        coroutine.on_error_stop_test = self.on_error_stop_test
        coroutine.on_error_stop_test_now = self.on_error_stop_test_now
        return coroutine

    def __register_started_coroutine(self, coroutine, greenlet):
        """存储所有的协程和 Greenlet对象，用于停止协程
        """
        self.all_coroutines[coroutine] = greenlet

    def __wait_coroutine_stopped(self, greenlet: Greenlet):
        """等待协程停止
        """
        if not greenlet.dead:
            greenlet.join(self.WAIT_TO_DIE)


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
        self.on_error_start_next_coroutine_loop = False
        self.on_error_start_next_current_loop = False
        self.on_error_break_current_loop = False
        self.on_error_stop_coroutine = False
        self.on_error_stop_test = False
        self.on_error_stop_test_now = False
        self.engine = engine
        self.local_vars = Variables()
        self.test_compiler: Union[TestCompiler, None] = None
        self.start_time = 0
        self.end_time = 0

        # 搜索 CoroutineGroupListener节点
        group_listener_searcher = SearchByClass(CoroutineGroupListener)
        self.group_tree.traverse(group_listener_searcher)
        self.coroutine_group_listeners = group_listener_searcher.get_search_result()

        # 搜索 TestIterationListener节点
        test_iteration_listener_searcher = SearchByClass(TestIterationListener)
        self.group_tree.traverse(test_iteration_listener_searcher)
        self.test_iteration_listeners = test_iteration_listener_searcher.get_search_result()

    def initial_context(self, context: CoroutineContext) -> None:
        """将父协程（运行 StandardEngine的协程）的本地变量赋值给子协程的本地变量中
        """
        self.local_vars.update(context.variables)

    def init_run(self, context: CoroutineContext) -> None:
        """
        协程执行前的初始化动作，包括以下动作：
        1、给 CoroutineContext赋值
        2、将 group层的非 Sampler节点和非 Controller节点传递给子代
        3、编译子代节点
        """
        context.variables = self.local_vars
        context.coroutine_number = self.coroutine_number
        context.variables.put(self.LAST_SAMPLE_OK, 'true')
        context.coroutine = self
        context.coroutine_group = self.coroutine_group
        context.engine = self.engine

        # 储存 group层的非 Sampler节点和非 Controller节点
        group_level_elements = self.group_tree.index(0).list()
        self.__remove_samplers_and_controllers(group_level_elements)

        # 编译 Group层下的所有子代节点
        self.test_compiler = TestCompiler(group_level_elements)
        self.group_tree.traverse(self.test_compiler)

        # 初始化协程组控制器
        self.coroutine_group.initialize()

        # 添加 Group层循环迭代监听器
        group_level_iteration_listener = self.GroupLevelIterationListener(self)
        self.coroutine_group.add_iteration_listener(group_level_iteration_listener)

        # 遍历执行 CoroutineGroupListener.group_started()
        self.__coroutine_started()

    def run(self):
        context = ContextService.get_context()
        try:
            self.init_run(context)

            while self.running:
                sampler = self.coroutine_group.next()

                while self.running and sampler is not None:
                    log.debug(
                        f'Next Sampler:[{sampler.name if isinstance(sampler, TestElement) else None}] '
                        f'class:[{sampler.__class__}]'
                    )
                    # 处理取样器
                    self.__process_sampler(sampler, context)
                    # 根据取样器控制循环
                    self.__control_loop_by_logical_action(sampler, context)
                    # 继续获取下一个取样器
                    sampler = self.coroutine_group.next()

                if self.coroutine_group.is_done:
                    self.running = False
                    log.info(f'协程 [{self.coroutine_name}] 已执行完成')

        except Exception:
            log.error(traceback.format_exc())
        finally:
            log.info(f'Coroutine finished: [{self.coroutine_name}]')
            self.__coroutine_finished()
            context.clear()
            ContextService.remove_context()

    def __coroutine_started(self) -> None:
        """
        协程开始时的动作
        1、ContextService统计协程数
        2、遍历执行 CoroutineGroupListener.group_started()
        """
        ContextService.incr_number_of_coroutines()
        for listener in self.coroutine_group_listeners:
            listener.group_started()

    def __coroutine_finished(self) -> None:
        """
        协程结束时的动作
        1、ContextService统计协程数
        2、遍历执行 CoroutineGroupListener.group_finished()
        """
        for listener in self.coroutine_group_listeners:
            listener.group_finished()
        ContextService.decr_number_of_coroutines()

    def __control_loop_by_logical_action(self, sampler: Sampler, context: CoroutineContext) -> None:
        last_sample_ok = context.variables.get(self.LAST_SAMPLE_OK)

        if not last_sample_ok and not self.on_error_continue:
            if self.on_error_start_next_coroutine_loop:
                log.debug('Last sample failed, starting next continue loop')
                self.__continue_on_coroutine_loop()

            elif self.on_error_start_next_current_loop:
                log.debug('Last sample failed, starting next current loop')
                self.__continue_on_current_loop(sampler)

            elif self.on_error_break_current_loop:
                log.debug('Last sample failed, breaking current loop')
                self.__break_on_current_loop(sampler)

            elif self.on_error_stop_coroutine:
                log.debug('Last sample failed, stoping coroutine')
                self.stop_coroutine()

            elif self.on_error_stop_test:
                log.debug('Last sample failed, stoping test')
                self.stop_test()

            elif self.on_error_stop_test_now:
                log.debug('Last sample failed, stoping test now')
                self.stop_test_now()

    def __process_sampler(self, current: Sampler, context: CoroutineContext) -> None:
        """
        执行取样器
        这里主要做异常捕获，以控制是否需要停止测试
        """
        try:
            if current:
                self.__execute_sample_package(current, context)
        except StopCoroutineException:
            log.error(traceback.format_exc())
        except StopTestException:
            log.error(traceback.format_exc())
        except StopTestNowException:
            log.error(traceback.format_exc())
        except Exception:
            log.error(traceback.format_exc())

    def __execute_sample_package(self, current: Sampler, context: CoroutineContext) -> None:
        """根据取样器的子代执行取样器
        """
        context.set_current_sampler(current)
        package = self.test_compiler.get_sample_package(current)

        # 执行前置处理器
        self.__run_pre_processors(package.pre_processors)

        # 执行时间控制器 todo 后续补充时间控制器
        # self.delay(pack.timers)

        # 执行取样器
        result = None
        if self.running:
            result = self.__do_sampling(current, context, package.listeners)

        if result:
            context.set_previous_result(result)

            # 执行后置处理器
            self.__run_post_processors(package.post_processors)

            # 执行断言
            self.__check_assertions(package.assertions, result, context)

            # 检查是否需要停止协程或测试
            if result.is_stop_coroutine or (not result.is_successful and self.on_error_stop_coroutine):
                self.stop_coroutine()
            if result.is_stop_test or (not result.is_successful and self.on_error_stop_test):
                self.stop_test()
            if result.is_stop_test_now or (not result.is_successful and self.on_error_stop_test_now):
                self.stop_test_now()

    def __do_sampling(self, sampler: Sampler, context: CoroutineContext, listeners: list) -> SampleResult:
        """执行取样器
        """
        sampler.context = context
        sampler.coroutine_name = self.coroutine_name

        # 遍历执行 SampleListener.sample_started(sample)
        for listener in listeners:
            listener.sample_started(sampler)

        result = None
        try:
            result = sampler.sample()
        except Exception:
            log.error(traceback.format_exc())
        finally:
            # 遍历执行 SampleListener.sample_ended(result)
            for listener in listeners:
                listener.sample_ended(result)

            return result

    def __check_assertions(self, assertions: list, result: SampleResult, context: CoroutineContext) -> None:
        """断言取样器结果
        """
        for assertion in assertions:
            self.__process_assertion(assertion, result)

        context.variables.put(self.LAST_SAMPLE_OK, result.is_successful)

    @staticmethod
    def __process_assertion(assertion, result: SampleResult) -> None:
        """执行断言
        """
        try:
            assertion_result = assertion.get_result(result)
            result.assertion_results.append(assertion_result)
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

    def __continue_on_coroutine_loop(self) -> None:
        self.coroutine_group.start_next_loop()

    def __continue_on_current_loop(self, sampler: Sampler) -> None:
        parent_controllers = self.__get_parent_controllers(sampler)

        for parent_controller in parent_controllers:
            if isinstance(parent_controller, CoroutineGroup):
                parent_controller.start_next_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.start_next_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def __break_on_current_loop(self, sampler: Sampler) -> None:
        parent_controllers = self.__get_parent_controllers(sampler)

        for parent_controller in parent_controllers:
            if isinstance(parent_controller, CoroutineGroup):
                parent_controller.break_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.break_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def __get_parent_controllers(self, sampler: Sampler) -> list:
        find_test_elements_up_to_root = FindTestElementsUpToRoot(sampler)
        self.group_tree.traverse(find_test_elements_up_to_root)
        return find_test_elements_up_to_root.get_controllers_to_root()

    def notify_test_listeners(self) -> None:
        self.local_vars.inc_iteration()
        for listener in self.test_iteration_listeners:
            listener.test_iteration_start(self.coroutine_group)

    def stop_coroutine(self) -> None:
        """停止协程
        """
        log.info(f'Stop Coroutine detected by coroutine: {self.coroutine_name}')
        self.running = False

    def stop_test(self) -> None:
        log.info(f'Stop Test detected by coroutine: {self.coroutine_name}')
        self.running = False
        if self.engine:
            self.engine.stop_test()

    def stop_test_now(self) -> None:
        log.info(f'Shutdown Test Now detected by coroutine: {self.coroutine_name}')
        self.running = False
        if self.engine:
            self.engine.stop_test_now()

    @staticmethod
    def __run_pre_processors(pre_processors: list) -> None:
        """执行前置处理器
        """
        for pre_processor in pre_processors:
            log.debug(f'Running preprocessor: {pre_processor.name}')
            pre_processor.process()

    @staticmethod
    def __run_post_processors(post_processors: list) -> None:
        """执行后置处理器
        """
        for post_processor in post_processors:
            log.debug(f'Running postprocessor: {post_processor.name}')
            post_processor.process()

    @staticmethod
    def __remove_samplers_and_controllers(elements: list) -> None:
        """删除 Sampler和 Controller节点
        """
        for element in elements[:]:
            if (
                    isinstance(element, Sampler) or
                    isinstance(element, Controller) or
                    not isinstance(element, TestElement)
            ):
                elements.remove(element)

    class GroupLevelIterationListener(LoopIterationListener):
        """Coroutine内部类，用于在协程组循环迭代开始时触发所有实现类的开始动作
        """

        def __init__(self, parent: "Coroutine"):
            self.parent = parent

        def iteration_start(self, source, iter_count) -> None:
            self.parent.notify_test_listeners()
