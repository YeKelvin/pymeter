#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group.py
# @Time    : 2020/2/13 12:58
# @Author  : Kelvin.Ye
import traceback
from enum import Enum
from enum import unique
from typing import Final
from typing import List
from typing import Union

from gevent import Greenlet

from taskmeter.assertions.assertion import AssertionResult
from taskmeter.common.exceptions import StopTaskGroupException
from taskmeter.common.exceptions import StopTestException
from taskmeter.common.exceptions import StopTestNowException
from taskmeter.controls.controller import Controller
from taskmeter.controls.controller import IteratingController
from taskmeter.controls.loop_controller import LoopController
from taskmeter.elements.element import TestElement
from taskmeter.engine.collection.traverser import FindTestElementsUpToRoot
from taskmeter.engine.collection.traverser import SearchByClass
from taskmeter.engine.collection.traverser import TestCompiler
from taskmeter.engine.collection.traverser import TreeCloner
from taskmeter.engine.collection.tree import HashTree
from taskmeter.engine.interface import TaskGroupListener
from taskmeter.engine.interface import LoopIterationListener
from taskmeter.engine.interface import TestIterationListener
from taskmeter.groups.context import ContextService
from taskmeter.groups.context import CoroutineContext
from taskmeter.groups.variables import Variables
from taskmeter.samplers.sample_result import SampleResult
from taskmeter.samplers.sampler import Sampler
from taskmeter.utils.log_util import get_logger


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
    STOP_COROUTINE_GROUP = 'stop_coroutine_group'

    # 错误时停止测试执行
    STOP_TEST = 'stop_test'

    # 错误时立即停止测试执行（中断协程）
    STOPTEST_NOW = 'stop_test_now'


class TaskGroup(LoopController):
    # Sampler失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR: Final = 'TaskGroup__on_sample_error'

    # 协程数
    NUMBER_COROUTINES: Final = 'TaskGroup__number_coroutines'

    # 每秒启动的协程数  todo 占坑，后面实现
    STARTUPS_PER_SECOND: Final = 'TaskGroup__startups_per_second'

    # 默认等待协程结束时间，单位 ms
    WAIT_TO_DIE = 5 * 1000

    @property
    def on_sample_error(self) -> str:
        return self.get_property_as_str(self.ON_SAMPLE_ERROR)

    @property
    def on_error_continue(self) -> bool:
        return self.on_sample_error == TestLogicalAction.CONTINUE.value

    @property
    def on_error_start_next_coroutine_loop(self) -> bool:
        return self.on_sample_error == TestLogicalAction.START_NEXT_COROUTINE_LOOP.value

    @property
    def on_error_start_next_current_loop(self) -> bool:
        return self.on_sample_error == TestLogicalAction.START_NEXT_CURRENT_LOOP.value

    @property
    def on_error_break_current_loop(self) -> bool:
        return self.on_sample_error == TestLogicalAction.BREAK_CURRENT_LOOP.value

    @property
    def on_error_stop_coroutine_group(self) -> bool:
        return self.on_sample_error == TestLogicalAction.STOP_COROUTINE_GROUP.value

    @property
    def on_error_stop_test(self) -> bool:
        return self.on_sample_error == TestLogicalAction.STOP_TEST.value

    @property
    def on_error_stop_test_now(self) -> bool:
        return self.on_sample_error == TestLogicalAction.STOPTEST_NOW.value

    @property
    def continue_forever(self) -> bool:
        return self.get_property_as_bool(self.CONTINUE_FOREVER)

    @property
    def loops(self) -> int:
        return self.get_property_as_int(self.LOOPS)

    @property
    def number_coroutines(self) -> int:
        return self.get_property_as_int(self.NUMBER_COROUTINES)

    @property
    def startups_per_second(self) -> float:
        return self.get_property_as_int(self.STARTUPS_PER_SECOND)

    def __init__(self, name: str = None, comments: str = None):
        super().__init__(name, comments)
        self.running = False
        self.group_number = None
        self.group_tree = None
        self.all_coroutines: List[Coroutine] = []

    def start(self, group_number, group_tree, engine) -> None:
        """启动TaskGroup

        Args:
            group_number:   group的序号
            group_tree:     group的HashTree
            engine:         Engine对象

        Returns: None

        """
        self.running = True
        self.group_number = group_number
        self.group_tree = group_tree
        context = ContextService.get_context()

        for coroutine_number in range(self.number_coroutines):
            if self.running:
                self.__start_new_coroutine(coroutine_number, engine, context)
            else:
                break

        log.info(f'已开始第 {self.group_number} 个协程组')

    def wait_coroutines_stopped(self) -> None:
        """等待所有协程停止
        """
        for coroutine in self.all_coroutines:
            if not coroutine.dead:
                coroutine.join(self.WAIT_TO_DIE)

    def stop_coroutines(self) -> None:
        """停止所有协程
        """
        self.running = False
        for coroutine in self.all_coroutines:
            coroutine.stop_coroutine()

    def kill_coroutines(self) -> None:
        """杀死所有协程
        """
        self.running = False
        for coroutine in self.all_coroutines:
            coroutine.stop_coroutine()
            coroutine.kill()  # todo 重写 kill方法，添加中断时的操作

    def __start_new_coroutine(self, coroutine_number, engine, context) -> 'Coroutine':
        """创建一个协程去执行协程组

        Args:
            coroutine_number:   协程的序号
            engine:             Engine对象
            context:            当前协程的 CoroutineContext对象

        Returns: Coroutine对象

        """
        coroutine = self.__make_coroutine(coroutine_number, engine, context)
        self.all_coroutines.append(coroutine)
        coroutine.start()
        return coroutine

    def __make_coroutine(self, coroutine_number, engine, context) -> 'Coroutine':
        """创建一个协程

        Args:
            coroutine_number:   协程的序号
            engine:             Engine对象
            context:            当前协程的 CoroutineContext对象

        Returns:

        """
        coroutine_name = f'{self.name} g{self.group_number}-c{coroutine_number + 1}'
        coroutine = Coroutine(self.__clone_group_tree())
        coroutine.initial_context(context)
        coroutine.coroutine_group = self
        coroutine.coroutine_number = coroutine_number
        coroutine.coroutine_name = coroutine_name
        coroutine.engine = engine
        coroutine.on_error_continue = self.on_error_continue
        coroutine.on_error_start_next_coroutine_loop = self.on_error_start_next_coroutine_loop
        coroutine.on_error_start_next_current_loop = self.on_error_start_next_current_loop
        coroutine.on_error_break_current_loop = self.on_error_break_current_loop
        coroutine.on_error_stop_coroutine_group = self.on_error_stop_coroutine_group
        coroutine.on_error_stop_test = self.on_error_stop_test
        coroutine.on_error_stop_test_now = self.on_error_stop_test_now
        return coroutine

    def __clone_group_tree(self) -> HashTree:
        """深拷贝 hashtree，目的是让每个协程持有不同的节点实例，在高并发下避免相互影响的问题
        """
        cloner = TreeCloner(True)
        self.group_tree.traverse(cloner)
        return cloner.get_cloned_tree()


class Coroutine(Greenlet):
    LAST_SAMPLE_OK = 'Coroutine.last_sample_ok'

    def __init__(self, group_tree: HashTree, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.group_tree = group_tree
        self.coroutine_group_loop_controller = group_tree.list()[0]
        self.coroutine_group = None
        self.coroutine_number = None
        self.coroutine_name = None
        self.engine = None
        self.on_error_continue = False
        self.on_error_start_next_coroutine_loop = False
        self.on_error_start_next_current_loop = False
        self.on_error_break_current_loop = False
        self.on_error_stop_coroutine_group = False
        self.on_error_stop_test = False
        self.on_error_stop_test_now = False
        self.local_vars = Variables()
        self.test_compiler: Union[TestCompiler, None] = None
        self.start_time = 0
        self.end_time = 0

        # 搜索TaskGroupListener节点
        group_listener_searcher = SearchByClass(TaskGroupListener)
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
        context.engine = self.engine
        context.coroutine = self
        context.coroutine_group = self.coroutine_group
        context.coroutine_number = self.coroutine_number
        context.coroutine_name = self.coroutine_name
        context.variables = self.local_vars
        context.variables.put(self.LAST_SAMPLE_OK, True)

        # 储存 group层的非 Sampler节点和非 Controller节点
        group_level_elements = self.group_tree.index(0).list()
        self.__remove_samplers_and_controllers(group_level_elements)

        # 编译 Group层下的所有子代节点
        self.test_compiler = TestCompiler(group_level_elements)
        self.group_tree.traverse(self.test_compiler)

        # 初始化协程组控制器
        self.coroutine_group_loop_controller.initialize()

        # 添加 Group层循环迭代监听器
        group_level_iteration_listener = self.GroupLevelIterationListener(self)
        self.coroutine_group_loop_controller.add_iteration_listener(group_level_iteration_listener)

        # 遍历执行 TaskGroupListener
        self.__coroutine_started()

    def _run(self):
        """协程组执行主体
        """
        context = ContextService.get_context()
        try:
            self.init_run(context)

            while self.running:
                sampler = self.coroutine_group_loop_controller.next()

                while self.running and sampler is not None:
                    log.debug(
                        f'coroutine:[ {self.coroutine_name} ] '
                        f'next sampler:[ {sampler.name if isinstance(sampler, TestElement) else None} ]'
                    )
                    # 处理取样器
                    self.__process_sampler(sampler, context)
                    # 根据取样器结果控制循环
                    self.__control_loop_by_logical_action(sampler, context)
                    # 继续获取下一个取样器
                    if self.running:
                        sampler = self.coroutine_group_loop_controller.next()

                if self.coroutine_group_loop_controller.is_done:
                    self.running = False
                    log.info(f'协程:[ {self.coroutine_name} ] 循环迭代已结束')

        except StopTaskGroupException:
            log.debug(
                f'coroutine:[ {self.coroutine_name} ] except StopTaskGroupException Exception, stoping coroutine'
            )
            self.stop_coroutine_group()
        except StopTestException:
            log.debug(f'coroutine:[ {self.coroutine_name} ] except StopTestException Exception, stoping test')
            self.stop_test()
        except StopTestNowException:
            log.debug(f'coroutine:[ {self.coroutine_name} ] except StopTestNowException Exception, stoping test now')
            self.stop_test_now()
        except Exception:
            log.error(traceback.format_exc())
        finally:
            log.info(f'协程:[ {self.coroutine_name} ] 已执行完成')
            # 遍历执行 TaskGroupListener
            self.__coroutine_finished()
            context.clear()
            ContextService.remove_context()

    def __coroutine_started(self) -> None:
        """
        协程开始时的动作
        1、ContextService统计协程数
        2、遍历执行TaskGroupListener
        """
        ContextService.incr_number_of_coroutines()
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all TaskGroupListener to start')
        for listener in self.coroutine_group_listeners:
            listener.group_started()

    def __coroutine_finished(self) -> None:
        """
        协程结束时的动作
        1、ContextService统计协程数
        2、遍历执行 TaskGroupListener
        """
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all TaskGroupListener to finish')
        for listener in self.coroutine_group_listeners:
            listener.group_finished()
        ContextService.decr_number_of_coroutines()

    def __control_loop_by_logical_action(self, sampler: Sampler, context: CoroutineContext) -> None:
        """取样器错误时，根据协程组的 on_sample_error选项，控制循环的动作
        """
        last_sample_ok = context.variables.get(self.LAST_SAMPLE_OK)

        # 取样器错误且非继续执行时，根据 on_sample_error选项控制循环迭代
        if not last_sample_ok and not self.on_error_continue:
            # 错误时开始下一个协程组循环
            if self.on_error_start_next_coroutine_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, starting next continue loop')
                self.__continue_on_coroutine_loop()

            # 错误时开始下一个当前控制器循环
            elif self.on_error_start_next_current_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, starting next current loop')
                self.__continue_on_current_loop(sampler)

            # 错误时中断当前控制器循环
            elif self.on_error_break_current_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, breaking current loop')
                self.__break_on_current_loop(sampler)

            # 错误时停止协程
            elif self.on_error_stop_coroutine_group:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping coroutine group')
                self.stop_coroutine_group()

            # 错误时停止测试
            elif self.on_error_stop_test:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping test')
                self.stop_test()

            # 错误时立即停止测试（中断所有协程）
            elif self.on_error_stop_test_now:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping test now')
                self.stop_test_now()

    def __process_sampler(self, sampler: Sampler, context: CoroutineContext) -> None:
        """执行取样器
        """
        if sampler:
            self.__execute_sample_package(sampler, context)

    def __execute_sample_package(self, sampler: Sampler, context: CoroutineContext) -> None:
        """根据取样器的子代执行取样器
        """
        context.set_current_sampler(sampler)
        log.debug(f'current sampler:[ {sampler.name} ] object:[ {sampler} ]')

        # 将 ConfigTestElement合并至取样器中
        package = self.test_compiler.configure_sampler(sampler)

        # 执行前置处理器
        self.__run_pre_processors(package.pre_processors)

        # 执行时间控制器 todo 后续补充时间控制器
        # self.delay(pack.timers)

        # 执行取样器
        result = None
        if self.running:
            result = self.__do_sampling(sampler, context, package.listeners)

        if result:
            context.set_previous_result(result)

            # 执行后置处理器
            self.__run_post_processors(package.post_processors)

            # 执行断言
            self.__check_assertions(package.assertions, result, context)

            # 检查是否需要停止协程或测试
            if result.is_stop_coroutine or (not result.success and self.on_error_stop_coroutine_group):
                log.info(f'协程:[ {self.coroutine_name} ] 用户主动设置停止协程组')
                self.stop_coroutine()
            if result.is_stop_test or (not result.success and self.on_error_stop_test):
                log.info(f'协程:[ {self.coroutine_name} ] 用户主动设置停止测试')
                self.stop_test()
            if result.is_stop_test_now or (not result.success and self.on_error_stop_test_now):
                log.info(f'协程:[ {self.coroutine_name} ] 用户主动设置立即停止测试')
                self.stop_test_now()

    def __do_sampling(self, sampler: Sampler, context: CoroutineContext, listeners: list) -> SampleResult:
        """执行取样器
        """
        sampler.context = context
        sampler.coroutine_name = self.coroutine_name

        # 遍历执行 SampleListener
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all SampleListener to start')
        for listener in listeners:
            listener.sample_started(sampler)

        result = None
        try:
            log.debug(f'sampler:[ {sampler.name} ] start to do sample')
            result = sampler.sample()
        except Exception:
            log.error(traceback.format_exc())
        finally:
            # 遍历执行 SampleListener
            log.debug(f'coroutine:[ {self.coroutine_name} ] notify all SampleListener to end')
            for listener in listeners:
                listener.sample_ended(result)

            return result

    def __check_assertions(self, assertions: list, result: SampleResult, context: CoroutineContext) -> None:
        """断言取样器结果
        """
        for assertion in assertions:
            self.__process_assertion(assertion, result)

        log.debug(
            f'coroutine:[ {self.coroutine_name} ] '
            f'last sampler:[ {result.sample_label} ] is {"ok" if result.success else "failed"}'
        )
        context.variables.put(self.LAST_SAMPLE_OK, result.success)

    def __process_assertion(self, assertion, result: SampleResult) -> None:
        """执行断言
        """
        try:
            assertion_result = assertion.get_result(result)
            result.assertion_results.append(assertion_result)
        except AssertionError as e:
            log.debug(f'coroutine:[ {self.coroutine_name} ] error processing Assertion: {e}')
            assertion_result = AssertionResult()
            assertion_result.is_failure = True
            assertion_result.failure_message = str(e)
        except RuntimeError as e:
            log.error(f'coroutine:[ {self.coroutine_name} ] error processing Assertion: {e}')
            assertion_result = AssertionResult()
            assertion_result.is_error = True
            assertion_result.failure_message = str(e)
        except Exception as e:
            log.error(f'coroutine:[ {self.coroutine_name} ] exception processing Assertion: {e}')
            log.error(traceback.format_exc())
            assertion_result = AssertionResult()
            assertion_result.is_error = True
            assertion_result.failure_message = str(e)

        result.success(result.success and not (assertion_result.is_Error or assertion_result.is_failure))
        result.assertion_result = assertion_result

    def __continue_on_coroutine_loop(self) -> None:
        """取样器错误时，继续 协程组控制器的循环
        """
        self.coroutine_group_loop_controller.start_next_loop()

    def __continue_on_current_loop(self, sampler: Sampler) -> None:
        """取样器错误时，继续取样器的父控制器循环
        """
        parent_controllers = self.__get_parent_controllers(sampler)

        for parent_controller in parent_controllers:
            if isinstance(parent_controller, TaskGroup):
                parent_controller.start_next_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.start_next_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def __break_on_current_loop(self, sampler: Sampler) -> None:
        """取样器错误时，中断取样器的父控制器循环
        """
        parent_controllers = self.__get_parent_controllers(sampler)

        for parent_controller in parent_controllers:
            if isinstance(parent_controller, TaskGroup):
                parent_controller.break_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.break_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def __get_parent_controllers(self, sampler: Sampler) -> list:
        """获取取样器的父控制器节点
        """
        find_test_elements_up_to_root = FindTestElementsUpToRoot(sampler)
        self.group_tree.traverse(find_test_elements_up_to_root)
        return find_test_elements_up_to_root.get_controllers_to_root()

    def _notify_test_iteration_listeners(self) -> None:
        """遍历执行 TestIterationListener
        """
        self.local_vars.inc_iteration()
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all TestIterationListener to start')
        for listener in self.test_iteration_listeners:
            listener.test_iteration_start(self.coroutine_group)

    def stop_coroutine(self) -> None:
        self.running = False

    def stop_coroutine_group(self) -> None:
        log.info(f'协程:[ {self.coroutine_name} ] 发起 Stop Coroutine Group 请求')
        self.coroutine_group.stop_coroutines()

    def stop_test(self) -> None:
        log.info(f'协程:[ {self.coroutine_name} ] 发起 Stop Test 请求')
        self.running = False
        if self.engine:
            self.engine.stop_test()

    def stop_test_now(self) -> None:
        log.info(f'协程:[ {self.coroutine_name} ] 发起 Stop Test Now 请求')
        self.running = False
        if self.engine:
            self.engine.stop_test_now()

    def __run_pre_processors(self, pre_processors: list) -> None:
        """执行前置处理器
        """
        for pre_processor in pre_processors:
            log.debug(f'coroutine:[ {self.coroutine_name} ] running preprocessor: {pre_processor.name}')
            pre_processor.process()

    def __run_post_processors(self, post_processors: list) -> None:
        """执行后置处理器
        """
        for post_processor in post_processors:
            log.debug(f'coroutine:[ {self.coroutine_name} ] running postprocessor: {post_processor.name}')
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

        def __init__(self, parent: 'Coroutine'):
            self.parent = parent

        def iteration_start(self, source, iter_count) -> None:
            self.parent._notify_test_iteration_listeners()
