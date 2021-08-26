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
from typing import Optional

from gevent import Greenlet

from pymeter.assertions.assertion import AssertionResult
from pymeter.common.exceptions import StopTestException
from pymeter.common.exceptions import StopTestGroupException
from pymeter.common.exceptions import StopTestNowException
from pymeter.controls.controller import Controller
from pymeter.controls.controller import IteratingController
from pymeter.controls.transaction import TransactionSampler
from pymeter.elements.element import TestElement
from pymeter.engine.interface import LoopIterationListener
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.engine.traverser import FindTestElementsUpToRoot
from pymeter.engine.traverser import FindTestElementsUpToRootTraverser
from pymeter.engine.traverser import SearchByClass
from pymeter.engine.traverser import TestCompiler
from pymeter.engine.traverser import TreeCloner
from pymeter.engine.tree import HashTree
from pymeter.groups.context import ContextService
from pymeter.groups.context import CoroutineContext
from pymeter.groups.package import SamplePackage
from pymeter.groups.variables import Variables
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


@unique
class LogicalAction(Enum):
    """Sampler失败时，下一步动作的逻辑枚举"""

    # 错误时继续
    CONTINUE = 'continue'

    # 错误时开始下一个协程控制器的循环
    START_NEXT_ITERATION_OF_COROUTINE = 'start_next_coroutine'

    # 错误时开始下一个当前控制器（协程控制器或子代控制器）的循环
    START_NEXT_ITERATION_OF_CURRENT_LOOP = 'start_next_current_loop'

    # 错误时中断当前控制器的循环
    BREAK_CURRENT_LOOP = 'break_current_loop'

    # 错误时停止协程
    STOP_TEST_GROUP = 'stop_test_group'

    # 错误时停止测试执行
    STOP_TEST = 'stop_test'

    # 错误时立即停止测试执行（中断协程）
    STOP_TEST_NOW = 'stop_test_now'


class TestGroup(Controller):

    # Sampler 失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR: Final = 'TestGroup__on_sample_error'

    # 协程数
    NUMBER_GROUPS: Final = 'TestGroup__number_groups'

    # TODO: 每秒启动的协程数
    STARTUPS_PER_SECOND: Final = 'TestGroup__startups_per_second'

    # 循环控制器
    MAIN_CONTROLLER: Final = 'TestGroup__main_controller'

    # 默认等待协程结束时间，单位 ms
    WAIT_TO_DIE = 5 * 1000

    @property
    def on_sample_error(self) -> str:
        return self.get_property_as_str(self.ON_SAMPLE_ERROR)

    @property
    def number_groups(self) -> int:
        return self.get_property_as_int(self.NUMBER_GROUPS)

    @property
    def startups_per_second(self) -> float:
        return self.get_property_as_int(self.STARTUPS_PER_SECOND)

    @property
    def main_controller(self) -> Controller:
        return self.get_property(self.MAIN_CONTROLLER).get_obj()

    @property
    def on_error_continue(self) -> bool:
        return self.on_sample_error == LogicalAction.CONTINUE.value

    @property
    def on_error_start_next_coroutine(self) -> bool:
        return self.on_sample_error == LogicalAction.START_NEXT_ITERATION_OF_COROUTINE.value

    @property
    def on_error_start_next_current_loop(self) -> bool:
        return self.on_sample_error == LogicalAction.START_NEXT_ITERATION_OF_CURRENT_LOOP.value

    @property
    def on_error_break_current_loop(self) -> bool:
        return self.on_sample_error == LogicalAction.BREAK_CURRENT_LOOP.value

    @property
    def on_error_stop_coroutine_group(self) -> bool:
        return self.on_sample_error == LogicalAction.STOP_TEST_GROUP.value

    @property
    def on_error_stop_test(self) -> bool:
        return self.on_sample_error == LogicalAction.STOP_TEST.value

    @property
    def on_error_stop_test_now(self) -> bool:
        return self.on_sample_error == LogicalAction.STOP_TEST_NOW.value

    def __init__(self):
        super().__init__()

        self.running = False
        self.group_number = None
        self.group_tree = None
        self.all_groups: List[Coroutine] = []

    def start(self, group_number, group_tree, engine) -> None:
        """启动TestGroup

        Args:
            group_number:   group 的序号
            group_tree:     group 的 HashTree
            engine:         Engine 对象

        Returns: None

        """
        self.running = True
        self.group_number = group_number
        self.group_tree = group_tree
        context = ContextService.get_context()

        for number in range(self.number_groups):
            if self.running:
                self.__start_new_group(number, engine, context)
            else:
                break

        log.info(f'开始第 {self.group_number} 个TestGroup')

    @property
    def done(self):
        """Controller API"""
        return self.main_controller.done

    @done.setter
    def done(self, value):
        """Controller API"""
        self.main_controller.done = value

    def next(self) -> Sampler:
        """Controller API"""
        return self.main_controller.next()

    def initialize(self):
        """Controller API"""
        self.main_controller.initialize()

    def trigger_end_of_loop(self):
        """Controller API"""
        self.main_controller.trigger_end_of_loop()

    def add_iteration_listener(self, listener):
        """Controller API"""
        self.main_controller.add_iteration_listener(listener)

    def remove_iteration_listener(self, listener):
        """Controller API"""
        self.main_controller.remove_iteration_listener(listener)

    def start_next_loop(self):
        """Controller API"""
        self.main_controller.start_next_loop()

    def add_test_element(self, child):
        """TestElement API"""
        self.main_controller.add_test_element(child)

    def wait_groups_stopped(self) -> None:
        """等待所有协程停止"""
        for group in self.all_groups:
            if not group.dead:
                group.join(self.WAIT_TO_DIE)

    def stop_coroutines(self) -> None:
        """停止所有协程"""
        self.running = False
        for group in self.all_groups:
            group.stop_coroutine()

    def kill_groups(self) -> None:
        """杀死所有协程"""
        self.running = False
        for group in self.all_groups:
            group.stop_coroutine()
            group.kill()  # TODO: 重写 kill方法，添加中断时的操作

    def __start_new_group(self, coroutine_number, engine, context) -> 'Coroutine':
        """创建一个协程去执行 TestGroup

        Args:
            coroutine_number:   协程的序号
            engine:             Engine 对象
            context:            当前协程的 CoroutineContext 对象

        Returns: Coroutine对象

        """
        coroutine = self.__make_coroutine(coroutine_number, engine, context)
        self.all_groups.append(coroutine)
        coroutine.start()
        return coroutine

    def __make_coroutine(self, coroutine_number, engine, context) -> 'Coroutine':
        """创建一个协程

        Args:
            coroutine_number:   协程的序号
            engine:             Engine对象
            context:            当前协程的 CoroutineContext 对象

        Returns:

        """
        coroutine_name = f'{self.name} g{self.group_number}-c{coroutine_number + 1}'
        coroutine = Coroutine(self.__clone_group_tree())
        coroutine.initial_context(context)
        coroutine.engine = engine
        coroutine.test_group = self
        coroutine.coroutine_number = coroutine_number
        coroutine.coroutine_name = coroutine_name
        coroutine.on_error_continue = self.on_error_continue
        coroutine.on_error_start_next_coroutine_loop = self.on_error_start_next_coroutine
        coroutine.on_error_start_next_current_loop = self.on_error_start_next_current_loop
        coroutine.on_error_break_current_loop = self.on_error_break_current_loop
        coroutine.on_error_stop_coroutine_group = self.on_error_stop_coroutine_group
        coroutine.on_error_stop_test = self.on_error_stop_test
        coroutine.on_error_stop_test_now = self.on_error_stop_test_now
        return coroutine

    def __clone_group_tree(self) -> HashTree:
        """深拷贝 HashTree，目的是让每个协程持有不同的节点实例，在高并发下避免相互影响的问题"""
        cloner = TreeCloner(True)
        self.group_tree.traverse(cloner)
        return cloner.get_cloned_tree()


class Coroutine(Greenlet):

    LAST_SAMPLE_OK = 'Gourp__last_sample_ok'

    def __init__(self, group_tree: HashTree, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.group_tree = group_tree
        self.test_group_controller: Controller = group_tree.list()[0]
        self.test_group: TestGroup = None
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
        self.test_compiler: Optional[TestCompiler] = None
        self.start_time = 0
        self.end_time = 0

        # 搜索 TestGroupListener 节点
        group_listener_searcher = SearchByClass(TestGroupListener)
        self.group_tree.traverse(group_listener_searcher)
        self.coroutine_group_listeners = group_listener_searcher.get_search_result()

        # 搜索 TestIterationListener 节点
        test_iteration_listener_searcher = SearchByClass(TestIterationListener)
        self.group_tree.traverse(test_iteration_listener_searcher)
        self.test_iteration_listeners = test_iteration_listener_searcher.get_search_result()

    def initial_context(self, context: CoroutineContext) -> None:
        """将父协程（运行 StandardEngine 的协程）的本地变量赋值给子协程的本地变量中"""
        self.local_vars.update(context.variables)

    def init_run(self, context: CoroutineContext) -> None:
        """
        协程执行前的初始化动作，包括以下动作：
            1、给 CoroutineContext 赋值
            2、将 Group 层的非 Sampler 节点和非 Controller 节点传递给子代
            3、编译子代节点
        """
        context.engine = self.engine
        context.coroutine = self
        context.coroutine_group = self.test_group
        context.coroutine_number = self.coroutine_number
        context.coroutine_name = self.coroutine_name
        context.variables = self.local_vars
        context.variables.put(self.LAST_SAMPLE_OK, True)

        # 储存 Group 层的非 Sampler 节点和非 Controller 节点
        group_level_elements = self.group_tree.index(0).list()
        self.__remove_samplers_and_controllers(group_level_elements)

        # 编译 Group 层下的所有子代节点
        log.info('开始编译TestGroup的子代节点')
        self.test_compiler = TestCompiler(group_level_elements)
        self.group_tree.traverse(self.test_compiler)
        log.debug(f'编译完成，sampler-package:[ {self.test_compiler.sampler_package_saver} ]')

        # 初始化 TestGroup 控制器
        self.test_group_controller.initialize()

        # 添加 Group 层循环迭代监听器
        group_level_iteration_listener = self.GroupLevelIterationListener(self)
        self.test_group_controller.add_iteration_listener(group_level_iteration_listener)

        # 遍历执行 TestGroupListener
        self.__coroutine_started()

    def _run(self):
        """TestGroup执行主体"""
        context = ContextService.get_context()
        try:
            self.init_run(context)

            while self.running:
                # 获取下一个 Sampler
                sampler = self.test_group_controller.next()

                while self.running and sampler:
                    log.debug(
                        f'coroutine:[ {self.coroutine_name} ] '
                        f'next-sampler:[ {sampler.name if isinstance(sampler, TestElement) else None} ]'
                    )
                    # 处理 Sampler
                    self.__process_sampler(sampler, None, context)
                    # 根据 Sampler 结果控制循环
                    self.__control_loop_by_logical_action(sampler, context)
                    # 获取下一个 Sampler
                    if self.running:
                        sampler = self.test_group_controller.next()

                if self.test_group_controller.done:
                    self.running = False
                    log.info(f'协程:[ {self.coroutine_name} ] 循环迭代已结束')

        except StopTestGroupException:
            log.debug(f'coroutine:[ {self.coroutine_name} ] except StopTestGroupException Exception, stoping coroutine')
            self.stop_group()
        except StopTestException:
            log.debug(f'coroutine:[ {self.coroutine_name} ] except StopTestException Exception, stoping test')
            self.stop_test()
        except StopTestNowException:
            log.debug(f'coroutine:[ {self.coroutine_name} ] except StopTestNowException Exception, stop test now')
            self.stop_test_now()
        except Exception:
            log.error(traceback.format_exc())
        finally:
            log.info(f'协程:[ {self.coroutine_name} ] 已执行完成')
            # 遍历执行TestGroupListener
            self.__coroutine_finished()
            context.clear()
            ContextService.remove_context()

    def __coroutine_started(self) -> None:
        """
        协程开始时的动作
            1、ContextService 统计协程数
            2、遍历执行 TestGroupListener
        """
        ContextService.incr_number_of_coroutines()
        log.debug(f'协程:[ {self.coroutine_name} ] notify all TestGroupListener to start')
        for listener in self.coroutine_group_listeners:
            listener.group_started()

    def __coroutine_finished(self) -> None:
        """
        协程结束时的动作
            1、ContextService 统计协程数
            2、遍历执行 TestGroupListener
        """
        log.debug(f'notify all TestGroupListener to finish, coroutine:[ {self.coroutine_name} ]')
        for listener in self.coroutine_group_listeners:
            listener.group_finished()
        ContextService.decr_number_of_coroutines()

    def __control_loop_by_logical_action(self, sampler: Sampler, context: CoroutineContext) -> None:
        """Sampler 失败时，根据 TestGroup 的 on_sample_error 选项，控制循环的动作"""
        last_sample_ok = context.variables.get(self.LAST_SAMPLE_OK)

        # Sampler 失败且非继续执行时，根据 on_sample_error 选项控制循环迭代
        if not last_sample_ok and not self.on_error_continue:
            # 错误时开始下一个 TestGroup 循环
            if self.on_error_start_next_coroutine_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, starting next continue loop')
                # self.__continue_on_coroutine_loop()
                self.__trigger_loop_logical_action_on_parent_controllers(
                    sampler, context, self.__continue_on_coroutine_loop
                )

            # 错误时开始下一个当前控制器循环
            elif self.on_error_start_next_current_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, starting next current loop')
                # self.__continue_on_current_loop(sampler)
                self.__trigger_loop_logical_action_on_parent_controllers(
                    sampler, context, self.__continue_on_current_loop
                )

            # 错误时中断当前控制器循环
            elif self.on_error_break_current_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, breaking current loop')
                # self.__break_on_current_loop(sampler)
                self.__trigger_loop_logical_action_on_parent_controllers(
                    sampler, context, self.__break_on_current_loop
                )

            # 错误时停止协程
            elif self.on_error_stop_coroutine_group:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping coroutine group')
                self.stop_group()

            # 错误时停止测试
            elif self.on_error_stop_test:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping test')
                self.stop_test()

            # 错误时立即停止测试（中断所有协程）
            elif self.on_error_stop_test_now:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping test now')
                self.stop_test_now()

    def __trigger_loop_logical_action_on_parent_controllers(self, sampler: Sampler, context: CoroutineContext, loop_action):
        transaction_sampler = None

        if isinstance(sampler, TransactionSampler):
            transaction_sampler = sampler

        real_sampler = self.find_real_sampler(sampler)

        if not real_sampler:
            raise RuntimeError(
                f'Got null subSampler calling findRealSampler for:[ {sampler.name if sampler else "None"} ], sampler:[ {sampler} ]'
            )

        # Find parent controllers of current sampler
        path_to_root_traverser = FindTestElementsUpToRootTraverser(real_sampler)
        self.group_tree.traverse(path_to_root_traverser)

        loop_action(path_to_root_traverser)

        # When using Start Next Loop option combined to TransactionController.
        # if an error occurs in a Sample (child of TransactionController)
        # then we still need to report the Transaction in error (and create the sample result)
        if transaction_sampler:
            transaction_package = self.test_compiler.configure_transaction_sampler(transaction_sampler)
            self.__do_end_transaction_sampler(transaction_sampler, None, transaction_package, context)

    def find_real_sampler(self, sampler: Sampler):
        real_sampler = sampler
        while isinstance(real_sampler, TransactionSampler):
            real_sampler = real_sampler.sub_sampler

        return real_sampler

    def __process_sampler(self, current: Sampler, parent: Sampler, context: CoroutineContext) -> None:
        """执行Sampler"""
        transaction_result = None
        transaction_sampler = None
        transaction_package = None

        if isinstance(current, TransactionSampler):
            transaction_sampler = current
            transaction_package = self.test_compiler.configure_transaction_sampler(transaction_sampler)

            # Check if the transaction is done
            if current.transaction_done:
                transaction_result = self.__do_end_transaction_sampler(
                    transaction_sampler, parent, transaction_package, context
                )
                # Transaction is done, we do not have a sampler to sample
                current = None
            else:
                prev = current
                # It is the sub sampler of the transaction that will be sampled
                current = transaction_sampler.sub_sampler
                if isinstance(current, TransactionSampler):
                    result = self.__process_sampler(current, prev, context)  # recursive call
                    context.setCurrentSampler(prev)
                    current = None
                    if result is not None:
                        transaction_sampler.add_sub_sampler_result(result)

        if current:
            self.__execute_sample_package(current, transaction_sampler, transaction_package, context)

        if (
            not self.running  # noqa
            and transaction_result is None  # noqa
            and transaction_sampler is not None  # noqa
            and transaction_package is not None  # noqa
        ):
            transaction_result = self.__do_end_transaction_sampler(
                transaction_sampler, parent, transaction_package, context
            )

        return transaction_result

    def __execute_sample_package(
        self, sampler: Sampler, transaction_sampler: TransactionSampler, transaction_package: SamplePackage,
        context: CoroutineContext
    ) -> None:
        """根据Sampler的子代执行Sampler"""
        log.debug(f'current-sampler:[ {sampler.name} ] object:[ {sampler} ]')
        context.set_current_sampler(sampler)

        package = self.test_compiler.configure_sampler(sampler)

        # 执行前置处理器
        self.__run_pre_processors(package.pre_processors)

        # TODO: 执行时间控制器
        # self.delay(pack.timers)

        # 执行 sampler
        result = None
        if self.running:
            result = self.__do_sampling(sampler, context, package.listeners)

        if result:
            # 设置为上一个结果
            context.set_previous_result(result)

            # 执行后置处理器
            self.__run_post_processors(package.post_processors)

            # 执行断言
            self.__check_assertions(package.assertions, result, context)

            # 遍历执行 SampleListener
            log.debug(f'notify all SampleListener to occurred, coroutine:[ {self.coroutine_name} ]')
            sample_listeners = self.__get_sample_listeners(package, transaction_package, transaction_sampler)
            for listener in sample_listeners:
                listener.sample_occurred(result)

            # Add the result as subsample of transaction if we are in a transaction
            if transaction_sampler:
                transaction_sampler.add_sub_sampler_result(result)

            # 检查是否需要停止协程或测试
            if result.stop_group or (not result.success and self.on_error_stop_coroutine_group):
                log.info(f'用户手动设置停止测试组，TestGroup:[ {self.coroutine_name} ]')
                self.stop_coroutine()
            if result.stop_test or (not result.success and self.on_error_stop_test):
                log.info(f'用户手动设置停止测试，TestGroup:[ {self.coroutine_name} ]')
                self.stop_test()
            if result.stop_test_now or (not result.success and self.on_error_stop_test_now):
                log.info(f'用户手动设置立即停止测试，TestGroup:[ {self.coroutine_name} ]')
                self.stop_test_now()

    def __do_sampling(self, sampler: Sampler, context: CoroutineContext, listeners: list) -> SampleResult:
        """执行Sampler"""
        # TODO: 给sampler设置context好像没啥用，可以ContextService获取
        sampler.context = context

        # 遍历执行 SampleListener
        log.debug(f'notify all SampleListener to start, coroutine:[ {self.coroutine_name} ]')
        for listener in listeners:
            listener.sample_started(sampler)

        result = None
        try:
            log.debug(f'start to do sample, sampler:[ {sampler.name} ]')
            result = sampler.sample()
        except Exception:
            log.error(traceback.format_exc())
        finally:
            # 遍历执行 SampleListener
            log.debug(f'notify all SampleListener to end, coroutine:[ {self.coroutine_name} ]')
            for listener in listeners:
                listener.sample_ended(result)

            return result

    def __do_end_transaction_sampler(
        self, sampler: TransactionSampler, parent: Sampler, package: SamplePackage, context: CoroutineContext
    ) -> SampleResult:
        # Get the transaction sample result
        result = sampler.transaction_sample_result

        # Check assertions for the transaction sample
        self.__check_assertions(package.assertions, result, context)

        #  Notify listeners with the transaction sample result
        if not isinstance(parent, TransactionSampler):
            # 遍历执行 SampleListener
            log.debug(f'notify all SampleListener to occurred, coroutine:[ {self.coroutine_name} ]')
            for listener in package.listeners:
                listener.sample_occurred(result)

        return result

    def __get_sample_listeners(
        self, sample_package: SamplePackage, transaction_package: SamplePackage, transaction_sampler: TransactionSampler
    ) -> List[SampleListener]:
        sampler_listeners = sample_package.listeners
        # Do not send subsamples to listeners which receive the transaction sample
        if transaction_sampler:
            only_subsampler_listeners = []
            for listener in sample_package.listeners:
                # Check if this instance is present in transaction listener list
                found = False
                for trans in transaction_package.listeners:
                    # Check for the same instance
                    if trans is listener:
                        found = True
                        break

                if not found:
                    only_subsampler_listeners.append(listener)

            sampler_listeners = only_subsampler_listeners

        return sampler_listeners

    def __check_assertions(self, assertions: list, result: SampleResult, context: CoroutineContext) -> None:
        """断言 Sampler 结果"""
        for assertion in assertions:
            self.__process_assertion(assertion, result)

        log.debug(
            f'coroutine:[ {self.coroutine_name} ] last-sampler:[ {result.sample_name} ] success:[ {result.success} ]'
        )
        context.variables.put(self.LAST_SAMPLE_OK, result.success)

    def __process_assertion(self, assertion, result: SampleResult) -> None:
        """执行断言"""
        try:
            assertion_result = assertion.get_result(result)
        except AssertionError as e:
            log.debug(f'coroutine:[ {self.coroutine_name} ] error processing Assertion: {e}')
            assertion_result = AssertionResult(result.sample_name)
            assertion_result.failure = True
            assertion_result.message = str(e)
        except RuntimeError as e:
            log.error(f'coroutine:[ {self.coroutine_name} ] error processing Assertion: {e}')
            assertion_result = AssertionResult(result.sample_name)
            assertion_result.error = True
            assertion_result.message = str(e)
        except Exception as e:
            log.error(f'coroutine:[ {self.coroutine_name} ] exception processing Assertion: {e}')
            log.error(traceback.format_exc())
            assertion_result = AssertionResult(result.sample_name)
            assertion_result.error = True
            assertion_result.message = traceback.format_exc()
        finally:
            result.success = result.success and not (assertion_result.error or assertion_result.failure)
            result.assertions.append(assertion_result)

    def __continue_on_coroutine_loop(self, path_to_root_traverser) -> None:
        """Sampler 失败时，继续 TestGroup 控制器的循环

        Executes a restart of Thread loop, equivalent of "continue" in algorithm but on Thread Loop.
        As a consequence it ends all loop on the path to root
        """
        # 改造前
        # self.test_group_controller.start_next_loop()
        # 改造后
        controllers_to_reinit = path_to_root_traverser.get_controllers_to_root()
        for parent_controller in controllers_to_reinit:
            if isinstance(parent_controller, TestGroup):
                parent_controller.start_next_loop()
            else:
                parent_controller.trigger_end_of_loop()

    def __continue_on_current_loop(self, path_to_root_traverser) -> None:
        """Sampler 失败时，继续 Sampler 的父控制器循环"""
        # 改造前
        # parent_controllers = self.__get_parent_controllers(sampler)
        # 改造后
        controllers_to_reinit = path_to_root_traverser.get_controllers_to_root()
        for parent_controller in controllers_to_reinit:
            if isinstance(parent_controller, TestGroup):
                parent_controller.start_next_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.start_next_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def __break_on_current_loop(self, path_to_root_traverser) -> None:
        """Sampler 失败时，中断 Sampler 的父控制器循环"""
        # 改造前
        # parent_controllers = self.__get_parent_controllers(sampler)
        # 改造后
        controllers_to_reinit = path_to_root_traverser.get_controllers_to_root()
        for parent_controller in controllers_to_reinit:
            if isinstance(parent_controller, TestGroup):
                parent_controller.break_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.break_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def __get_parent_controllers(self, sampler: Sampler) -> list:
        """获取 Sampler 的父控制器节点"""
        find_test_elements_up_to_root = FindTestElementsUpToRoot(sampler)
        self.group_tree.traverse(find_test_elements_up_to_root)
        return find_test_elements_up_to_root.get_controllers_to_root()

    def _notify_test_iteration_listeners(self) -> None:
        """遍历执行 TestIterationListener"""
        self.local_vars.inc_iteration()
        log.debug(f'notify all TestIterationListener to start, coroutine:[ {self.coroutine_name} ]')
        for listener in self.test_iteration_listeners:
            listener.test_iteration_start(self.test_group)

    def stop_coroutine(self) -> None:
        self.running = False

    def stop_group(self) -> None:
        log.info(f'协程发起 StopCoroutineGroup 请求，协程名称:[ {self.coroutine_name} ]')
        self.test_group.stop_coroutines()

    def stop_test(self) -> None:
        log.info(f'协程发起 StopTestCollection 请求，协程名称:[ {self.coroutine_name} ] ')
        self.running = False
        if self.engine:
            self.engine.stop_test()

    def stop_test_now(self) -> None:
        log.info(f'协程发起 StopTestCollectionNow 请求，协程名称:[ {self.coroutine_name} ] ')
        self.running = False
        if self.engine:
            self.engine.stop_test_now()

    def __run_pre_processors(self, pre_processors: list) -> None:
        """执行前置处理器"""
        for pre_processor in pre_processors:
            log.debug(f'coroutine:[ {self.coroutine_name} ] running-pre-processor: {pre_processor.name}')
            pre_processor.process()

    def __run_post_processors(self, post_processors: list) -> None:
        """执行后置处理器"""
        for post_processor in post_processors:
            log.debug(f'coroutine:[ {self.coroutine_name} ] running-post-processor: {post_processor.name}')
            post_processor.process()

    @staticmethod
    def __remove_samplers_and_controllers(elements: list) -> None:
        """删除 Sampler 和 Controller 节点"""
        for element in elements[:]:
            if isinstance(element, Sampler):
                elements.remove(element)
            if isinstance(element, Controller):
                elements.remove(element)
            if not isinstance(element, TestElement):
                elements.remove(element)

    class GroupLevelIterationListener(LoopIterationListener):
        """Coroutine 内部类，用于在 TestGroup 循环迭代开始时触发所有实现类的开始动作"""

        def __init__(self, parent: 'Coroutine'):
            self.parent = parent

        def iteration_start(self, source, iter_count) -> None:
            self.parent._notify_test_iteration_listeners()


class SetupThreadGroup(TestGroup):
    ...


class TearDownThreadGroup(TestGroup):
    ...
