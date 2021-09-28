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
from pymeter.controls.loop_controller import LoopController
from pymeter.controls.transaction import TransactionSampler
from pymeter.elements.element import TestElement
from pymeter.engine.interface import LoopIterationListener
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCompilerHelper
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.engine.traverser import FindTestElementsUpToRoot
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


class TestGroup(Controller, TestCompilerHelper):

    # Sampler 失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR = 'TestGroup__on_sample_error'

    # 协程数
    NUMBER_GROUPS = 'TestGroup__number_groups'

    # TODO: 每秒启动的协程数
    STARTUPS_PER_SECOND = 'TestGroup__startups_per_second'

    # 循环控制器
    MAIN_CONTROLLER = 'TestGroup__main_controller'

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
    def main_controller(self) -> LoopController:
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
        self.groups: List[Coroutine] = []
        self.children: List[TestElement] = []

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

    def break_loop(self):
        """Controller API"""
        self.main_controller.break_loop()

    def add_test_element(self, child):
        """TestElement API"""
        self.main_controller.add_test_element(child)

    def add_test_element_once(self, child) -> bool:
        """@override from TestCompilerHelper"""
        if child not in self.children:
            self.children.append(child)
            self.add_test_element(child)
            return True
        else:
            return False

    def wait_groups_stopped(self) -> None:
        """等待所有协程停止"""
        for group in self.groups:
            if not group.dead:
                group.join(self.WAIT_TO_DIE)

    def stop_coroutines(self) -> None:
        """停止所有协程"""
        self.running = False
        for group in self.groups:
            group.stop_coroutine()

    def kill_groups(self) -> None:
        """杀死所有协程"""
        self.running = False
        for group in self.groups:
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
        self.groups.append(coroutine)
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
        coroutine.group = self
        coroutine.coroutine_number = coroutine_number
        coroutine.coroutine_name = coroutine_name
        return coroutine

    def __clone_group_tree(self) -> HashTree:
        """深拷贝 HashTree，目的是让每个协程持有不同的节点实例，在高并发下避免相互影响的问题"""
        cloner = TreeCloner(True)
        self.group_tree.traverse(cloner)
        return cloner.get_cloned_tree()


class Coroutine(Greenlet):

    LAST_SAMPLE_OK: Final = 'Coroutine__last_sample_ok'

    def __init__(self, group_tree: HashTree, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = None
        self.running = True
        self.group: TestGroup = None
        self.group_main_controller: Controller = group_tree.list()[0]
        self.group_tree = group_tree
        self.coroutine_name = None
        self.coroutine_number = None
        self.compiler: TestCompiler = TestCompiler(self.group_tree)
        self.variables = Variables()
        self.start_time = 0
        self.end_time = 0

        # 搜索 TestGroupListener 节点
        group_listener_searcher = SearchByClass(TestGroupListener)
        self.group_tree.traverse(group_listener_searcher)
        self.group_listeners = group_listener_searcher.get_search_result()

        # 搜索 TestIterationListener 节点
        test_iteration_listener_searcher = SearchByClass(TestIterationListener)
        self.group_tree.traverse(test_iteration_listener_searcher)
        self.test_iteration_listeners = test_iteration_listener_searcher.get_search_result()

    def initial_context(self, context: CoroutineContext) -> None:
        """将父协程（运行 StandardEngine 的协程）的局部变量赋值给子协程的局部变量中"""
        self.variables.update(context.variables)

    def init_run(self, context: CoroutineContext) -> None:
        """
        协程执行前的初始化动作，包括以下动作：
            1、给 CoroutineContext 赋值
            2、将 TestGroup 的非 Sampler/Controller 节点传递给子代
            3、编译子代节点
        """
        context.engine = self.engine
        context.group = self.group
        context.coroutine = self
        context.coroutine_number = self.coroutine_number
        context.coroutine_name = self.coroutine_name
        context.variables = self.variables
        context.variables.put(self.LAST_SAMPLE_OK, True)

        # 编译 TestGroup 的子代节点
        log.info('开始编译 TestGroup 节点')
        self.group_tree.traverse(self.compiler)

        # 初始化 TestGroup 控制器
        self.group_main_controller.initialize()

        # 添加 TestGroup 循环迭代监听器
        group_level_iteration_listener = self.IterationListener(self)
        self.group_main_controller.add_iteration_listener(group_level_iteration_listener)

        # 遍历执行 TestGroupListener
        self.__coroutine_started()

    def _run(self, *args, **kwargs):
        """执行协程的入口"""
        context = ContextService.get_context()

        try:
            self.init_run(context)

            while self.running:
                # 获取下一个 Sampler
                sampler = self.group_main_controller.next()

                while self.running and sampler:
                    log.debug(f'coroutine:[ {self.coroutine_name} ] current sampler:[ {sampler} ]')
                    # 处理 Sampler
                    self.__process_sampler(sampler, None, context)
                    # 根据 Sampler 结果控制循环
                    self.__control_loop_by_logical_action(sampler, context)
                    # 获取下一个 Sampler
                    if self.running:
                        sampler = self.group_main_controller.next()

                if self.group_main_controller.done:
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
            # 遍历执行 TestGroupListener
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
        for listener in self.group_listeners:
            listener.group_started()

    def __coroutine_finished(self) -> None:
        """
        协程结束时的动作
            1、ContextService 统计协程数
            2、遍历执行 TestGroupListener
        """
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all TestGroupListener to finish')
        for listener in self.group_listeners:
            listener.group_finished()
        ContextService.decr_number_of_coroutines()

    def __control_loop_by_logical_action(self, sampler: Sampler, context: CoroutineContext) -> None:
        """Sampler 失败时，根据 TestGroup 的 on_sample_error 选项，控制循环的动作"""
        last_sample_ok = context.variables.get(self.LAST_SAMPLE_OK)

        # Sampler 失败且非继续执行时，根据 on_sample_error 选项控制循环迭代
        if not last_sample_ok and not self.group.on_error_continue:
            # 错误时开始下一个 TestGroup 循环
            if self.group.on_error_start_next_coroutine:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, starting next continue loop')
                self.__trigger_loop_logical_action_on_parent_controllers(
                    sampler, context, self.__continue_on_coroutine_loop
                )

            # 错误时开始下一个当前控制器循环
            elif self.group.on_error_start_next_current_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, starting next current loop')
                self.__trigger_loop_logical_action_on_parent_controllers(
                    sampler, context, self.__continue_on_current_loop
                )

            # 错误时中断当前控制器循环
            elif self.group.on_error_break_current_loop:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, breaking current loop')
                self.__trigger_loop_logical_action_on_parent_controllers(
                    sampler, context, self.__break_on_current_loop
                )

            # 错误时停止协程
            elif self.group.on_error_stop_coroutine_group:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping coroutine group')
                self.stop_group()

            # 错误时停止测试
            elif self.group.on_error_stop_test:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping test')
                self.stop_test()

            # 错误时立即停止测试（中断所有协程）
            elif self.group.on_error_stop_test_now:
                log.debug(f'coroutine:[ {self.coroutine_name} ] last sample failed, stoping test now')
                self.stop_test_now()

    def __trigger_loop_logical_action_on_parent_controllers(
            self, sampler: Sampler, context: CoroutineContext, loop_action
    ):
        transaction_sampler = None

        if isinstance(sampler, TransactionSampler):
            transaction_sampler = sampler

        real_sampler = self.__find_real_sampler(sampler)

        if not real_sampler:
            raise RuntimeError(
                f'Got null subSampler calling findRealSampler for:[ {sampler} ], sampler:[ {sampler} ]'
            )

        # 查找父级 Controllers
        path_to_root_traverser = FindTestElementsUpToRoot(real_sampler)
        self.group_tree.traverse(path_to_root_traverser)

        loop_action(path_to_root_traverser)

        # When using Start Next Loop option combined to TransactionController.
        # if an error occurs in a Sample (child of TransactionController)
        # then we still need to report the Transaction in error (and create the sample result)
        if transaction_sampler:
            transaction_package = self.compiler.configure_transaction_sampler(transaction_sampler)
            self.__do_end_transaction_sampler(transaction_sampler, None, transaction_package, context)

    def __find_real_sampler(self, sampler: Sampler):
        real_sampler = sampler
        while isinstance(real_sampler, TransactionSampler):
            real_sampler = real_sampler.sub_sampler

        return real_sampler

    def __process_sampler(
            self, current: Sampler, parent: Optional[Sampler], context: CoroutineContext
    ) -> Optional[SampleResult]:
        """执行 Sampler"""
        transaction_result = None
        transaction_sampler = None
        transaction_package = None

        if isinstance(current, TransactionSampler):
            transaction_sampler = current
            transaction_package = self.compiler.configure_transaction_sampler(transaction_sampler)
            log.debug(f'transaction package:[ {transaction_package} ]')

            # 检查事务是否已完成
            if current.transaction_done:
                transaction_result = self.__do_end_transaction_sampler(
                    transaction_sampler, parent, transaction_package, context
                )
                # 事务已完成，Sampler 无需继续执行
                current = None
            else:
                prev = current
                current = transaction_sampler.sub_sampler
                if isinstance(current, TransactionSampler):
                    result = self.__process_sampler(current, prev, context)  # 递归处理
                    context.set_current_sampler(prev)
                    current = None  # 当前 Sampler 为事务，无需继续执行
                    if result:
                        transaction_sampler.add_sub_sampler_result(result)

        # 执行 Sampler 和 SamplerPackage，不包含 TransactionSampler
        if current:
            self.__execute_sample_package(current, transaction_sampler, transaction_package, context)

        # 协程已经停止运行但事务未生成结果时，手动结束事务
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
        self,
        sampler: Sampler,
        transaction_sampler: TransactionSampler,
        transaction_package: SamplePackage,
        context: CoroutineContext
    ) -> None:
        """执行 Sampler 和 SamplerPackage"""

        context.set_current_sampler(sampler)

        package = self.compiler.configure_sampler(sampler)
        log.debug(f'samplerPackage:[ {package} ]')

        # 执行前置处理器
        self.__run_pre_processors(package.pre_processors)

        # TODO: 执行时间控制器
        # self.delay(pack.timers)

        # 执行取样器
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
            log.debug(f'coroutine:[ {self.coroutine_name} ] notify all SampleListener to occurred')
            sample_listeners = self.__get_sample_listeners(package, transaction_package, transaction_sampler)
            for listener in sample_listeners:
                listener.sample_occurred(result)

            self.compiler.done(package)

            # Add the result as subsample of transaction if we are in a transaction
            if transaction_sampler:
                transaction_sampler.add_sub_sampler_result(result)

            # 检查是否需要停止协程或测试
            if result.stop_group or (not result.success and self.group.on_error_stop_coroutine_group):
                log.info(f'用户手动设置停止测试组，TestGroup:[ {self.coroutine_name} ]')
                self.stop_coroutine()
            if result.stop_test or (not result.success and self.group.on_error_stop_test):
                log.info(f'用户手动设置停止测试，TestGroup:[ {self.coroutine_name} ]')
                self.stop_test()
            if result.stop_test_now or (not result.success and self.group.on_error_stop_test_now):
                log.info(f'用户手动设置立即停止测试，TestGroup:[ {self.coroutine_name} ]')
                self.stop_test_now()
        else:
            self.compiler.done(package)

    def __do_sampling(self, sampler: Sampler, context: CoroutineContext, listeners: list) -> SampleResult:
        """执行Sampler"""
        # TODO: 给sampler设置context好像没啥用，可以ContextService获取
        sampler.context = context

        # 遍历执行 SampleListener
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all SampleListener to start')
        for listener in listeners:
            listener.sample_started(sampler)

        result = None
        try:
            log.debug(f'doing sample, sampler:[ {sampler} ]')
            result = sampler.sample()
        except Exception:
            log.error(traceback.format_exc())
            # TODO: 将异常堆栈写入SampleResult
        finally:
            # 遍历执行 SampleListener
            log.debug(f'coroutine:[ {self.coroutine_name} ] notify all SampleListener to end')
            for listener in listeners:
                listener.sample_ended(result)

            return result

    def __do_end_transaction_sampler(
        self,
        transaction_sampler: TransactionSampler,
        parent: Optional[Sampler],
        transaction_package: SamplePackage,
        context: CoroutineContext
    ) -> SampleResult:
        log.debug(
            f'coroutine:[ {self.coroutine_name} ] do end transaction:[ {transaction_sampler} ] parent:[ {parent} ]'
        )

        # Get the transaction sample result
        result = transaction_sampler.transaction_sample_result

        # Check assertions for the transaction sample
        self.__check_assertions(transaction_package.assertions, result, context)

        #  Notify listeners with the transaction sample result
        if not isinstance(parent, TransactionSampler):
            # 遍历执行 SampleListener
            log.debug(f'coroutine:[ {self.coroutine_name} ] notify all SampleListener to occurred')
            log.debug(f'transaction sampler listeners:{transaction_package.listeners}')
            for listener in transaction_package.listeners:
                listener.sample_occurred(result)

        self.compiler.done(transaction_package)
        return result

    def __check_assertions(self, assertions: list, result: SampleResult, context: CoroutineContext) -> None:
        """断言 Sampler 结果"""
        for assertion in assertions:
            self.__process_assertion(assertion, result)

        log.debug(
            f'coroutine:[ {self.coroutine_name} ] last sampler:[ {result.sample_name} ] success:[ {result.success} ]'
        )
        context.variables.put(self.LAST_SAMPLE_OK, result.success)

    def __process_assertion(self, assertion, result: SampleResult) -> None:
        """执行断言"""
        assertion_result = None
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

    def __get_sample_listeners(
        self, sample_package: SamplePackage, transaction_package: SamplePackage, transaction_sampler: TransactionSampler
    ) -> List[SampleListener]:
        sampler_listeners = sample_package.listeners
        # Do not send subsamples to listeners which receive the transaction sample
        if transaction_sampler:
            only_subsampler_listeners = []
            for listener in sample_package.listeners:
                # 检查在 TransactionListenerList 中是否有重复的 listener
                found = False
                for trans in transaction_package.listeners:
                    # 过滤相同的 listener
                    if trans is listener:
                        found = True
                        break

                if not found:
                    only_subsampler_listeners.append(listener)

            sampler_listeners = only_subsampler_listeners

        return sampler_listeners

    def __continue_on_coroutine_loop(self, path_to_root_traverser) -> None:
        """Sampler 失败时，继续 TestGroup 控制器的循环"""
        controllers_to_reinit = path_to_root_traverser.get_controllers_to_root()
        for parent_controller in controllers_to_reinit:
            if isinstance(parent_controller, TestGroup):
                parent_controller.start_next_loop()
            else:
                parent_controller.trigger_end_of_loop()

    def __continue_on_current_loop(self, path_to_root_traverser) -> None:
        """Sampler 失败时，继续 Sampler 的父控制器循环"""
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
        controllers_to_reinit = path_to_root_traverser.get_controllers_to_root()
        for parent_controller in controllers_to_reinit:
            if isinstance(parent_controller, TestGroup):
                parent_controller.break_loop()
            elif isinstance(parent_controller, IteratingController):
                parent_controller.break_loop()
                break
            else:
                parent_controller.trigger_end_of_loop()

    def _notify_test_iteration_listeners(self) -> None:
        """遍历执行 TestIterationListener"""
        log.debug(f'coroutine:[ {self.coroutine_name} ] notify all TestIterationListener to start')
        self.variables.inc_iteration()
        for listener in self.test_iteration_listeners:
            listener.test_iteration_start(self.group_main_controller, self.variables.iteration)
            if isinstance(listener, TestElement):
                listener.recover_running_version()

    def stop_coroutine(self) -> None:
        self.running = False

    def stop_group(self) -> None:
        log.info(f'coroutine:[ {self.coroutine_name} ] 协程发起 StopCoroutineGroup 请求')
        self.group.stop_coroutines()

    def stop_test(self) -> None:
        log.info(f'coroutine:[ {self.coroutine_name} ] 协程发起 StopTestCollection 请求')
        self.running = False
        if self.engine:
            self.engine.stop_test()

    def stop_test_now(self) -> None:
        log.info(f'coroutine:[ {self.coroutine_name} ] 协程发起 StopTestCollectionNow 请求')
        self.running = False
        if self.engine:
            self.engine.stop_test_now()

    def __run_pre_processors(self, pre_processors: list) -> None:
        """执行前置处理器"""
        for pre_processor in pre_processors:
            log.debug(f'coroutine:[ {self.coroutine_name} ] running preProcessor: {pre_processor.name}')
            pre_processor.process()

    def __run_post_processors(self, post_processors: list) -> None:
        """执行后置处理器"""
        for post_processor in post_processors:
            log.debug(f'coroutine:[ {self.coroutine_name} ] running postProcessor: {post_processor.name}')
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

    class IterationListener(LoopIterationListener):
        """Coroutine 内部类，用于在 TestGroup 循环迭代开始时触发所有实现类的开始动作"""

        def __init__(self, parent: 'Coroutine'):
            self.parent = parent

        def iteration_start(self, source, iter) -> None:
            self.parent._notify_test_iteration_listeners()


class SetupGroup(TestGroup):

    # Sampler 失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR: Final = 'SetupGroup__on_sample_error'

    # 协程数
    NUMBER_GROUPS: Final = 'SetupGroup__number_groups'

    # 每秒启动的协程数
    STARTUPS_PER_SECOND: Final = 'SetupGroup__startups_per_second'

    # 循环控制器
    MAIN_CONTROLLER: Final = 'SetupGroup__main_controller'


class TearDownGroup(TestGroup):

    # Sampler 失败时的处理动作，枚举 LogicalAction
    ON_SAMPLE_ERROR: Final = 'TearDownGroup__on_sample_error'

    # 协程数
    NUMBER_GROUPS: Final = 'TearDownGroup__number_groups'

    # 每秒启动的协程数
    STARTUPS_PER_SECOND: Final = 'TearDownGroup__startups_per_second'

    # 循环控制器
    MAIN_CONTROLLER: Final = 'TearDownGroup__main_controller'
