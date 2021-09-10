#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import logging
import traceback

from gevent import Greenlet

from pymeter.common.exceptions import EngineException
from pymeter.common.exceptions import StopTestException
from pymeter.elements.element import TestElement
from pymeter.engine.collection import TestCollection
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.traverser import SearchByClass
from pymeter.engine.tree import HashTree
from pymeter.groups.context import ContextService
from pymeter.groups.group import SetupGroup
from pymeter.groups.group import TearDownGroup
from pymeter.groups.group import TestGroup
from pymeter.listeners.result_collector import ResultCollector
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class StandardEngine(Greenlet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = None
        self.running = False
        self.active = False
        self.tree = None
        self.serialized = True  # 标识 TestGroup 是否顺序运行
        self.groups = []  # 储存已启动的 TestGroup
        self.collection: TestCollection = None

    def configure(self, tree: HashTree) -> None:
        """将脚本配置到执行引擎中
        """
        # 查找脚本顶层列表中的 TestCollection 对象
        searcher = SearchByClass(TestCollection)
        tree.traverse(searcher)
        collections = searcher.get_search_result()

        if len(collections) == 0:
            raise EngineException('TestCollection数量少于1，请确保至少存在一个TestCollection')

        self.collection = collections[0]
        self.serialized = self.collection.serialized
        self.active = True
        self.tree = tree

    def run_test(self) -> None:
        """执行脚本，这里主要做异常捕获"""
        try:
            self.start()
            self.join()  # 等待主协程结束
        except EngineException:
            log.error(traceback.format_exc())

    def _run(self) -> None:
        """脚本执行主体"""
        log.info('开始执行脚本')
        self.running = True

        self.id = f'{id(self)} - {self.minimal_ident}'
        ContextService.get_context().engine = self
        ContextService.start_test()

        # 查找 TestCollectionListener 对象
        test_listener_searcher = SearchByClass(TestCollectionListener)
        self.tree.traverse(test_listener_searcher)

        # 遍历执行 TestCollectionListener
        self.__notify_test_listeners_of_start(test_listener_searcher)

        # 存储 TestCollection 子代节点(非 TestGroup 节点)
        collection_level_elements = self.tree.index(0).list()
        self.__remove_groups(collection_level_elements)  # 删除 TestGroup 节点

        # 查找 SetupGroup / TestGroup / TearDownGroup 对象
        setup_group_searcher = SearchByClass(SetupGroup)
        group_searcher = SearchByClass(TestGroup)
        teardown_group_searcher = SearchByClass(TearDownGroup)

        self.tree.traverse(setup_group_searcher)
        self.tree.traverse(group_searcher)
        self.tree.traverse(teardown_group_searcher)

        setup_group_iter = iter(setup_group_searcher.get_search_result())
        group_iter = iter(group_searcher.get_search_result())
        teardown_group_iter = iter(teardown_group_searcher.get_search_result())

        group_count = 0
        ContextService.clear_total_coroutines(self.id)  # TODO: 还要修改

        # ####################################################################################################
        # SetUpGroup 运行主体
        # ####################################################################################################
        while self.running:
            log.info('Starting setUp groups')
            try:
                setup_group: SetupGroup = next(setup_group_iter)
                group_count += 1
                group_name = setup_group.name
                log.info(f'开始第 {group_count} 个 SetUpGroup，group:[ {group_name} ]')
                self.__start_task_group(setup_group, group_count, setup_group_searcher, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    log.info(f'开始下一个 SetUpGroup 之前等待当前 SetUpGroup 完成，group:[ {group_name} ]')
                    setup_group.wait_groups_stopped()
            except StopIteration:
                log.info('所有 SetUpGroup 已启动')
                break

        log.info('Waiting for all setup groups to exit')
        self.__wait_groups_stopped()
        log.info('All SetupGroups have ended')
        group_count = 0
        ContextService.clear_total_coroutines(self.id)
        self.groups.clear()  # The groups have all completed now

        # ####################################################################################################
        # TestGroup 运行主体
        # ####################################################################################################
        while self.running:
            log.info(f'开始执行TestGroup，执行方式:[ {"顺序" if self.serialized else "并行"}执行 ]')
            try:
                group: TestGroup = next(group_iter)
                if isinstance(group, SetupGroup) or isinstance(group, TearDownGroup):
                    continue
                group_count += 1
                group_name = group.name
                log.info(f'开始第 {group_count} 个TestGroup，group:[ {group_name} ]')
                self.__start_task_group(group, group_count, group_searcher, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    log.info(f'开始下一个TestGroup之前等待当前TestGroup完成，group:[ {group_name} ]')
                    group.wait_groups_stopped()
            except StopIteration:
                log.info('所有 TestGroup 已启动')
                break

        if group_count == 0:
            log.warning('TestCollection下找不到已启用的TestGroup或所有TestGroup已被禁用')
        else:
            if not self.running:
                log.info('测试已停止，不再启动剩余的TestGroup')
            if not self.serialized:
                log.info('等待所有TestGroup执行完成')

        log.info('Waiting for all test groups to exit')
        self.__wait_groups_stopped()
        log.info('All TestGroups have ended')
        group_count = 0
        ContextService.clear_total_coroutines(self.id)
        self.groups.clear()  # The groups have all completed now

        # ####################################################################################################
        # TeardownGroup 运行主体
        # ####################################################################################################
        while self.running:
            log.info('Starting teardown groups')
            try:
                teardown_group: TearDownGroup = next(teardown_group_iter)
                group_count += 1
                group_name = teardown_group.name
                log.info(f'开始第 {group_count} 个 TearDownGroup，group:[ {group_name} ]')
                self.__start_task_group(teardown_group, group_count, teardown_group_iter, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    log.info(f'开始下一个 TearDownGroup 之前等待当前 TearDownGroup 完成，group:[ {group_name} ]')
                    setup_group.wait_groups_stopped()
            except StopIteration:
                log.info('所有 TearDownGroup 已启动')
                break

        log.info('Waiting for all teardown groups to exit')
        self.__wait_groups_stopped()
        log.info('All TearDownGroups have ended')
        group_count = 0
        ContextService.clear_total_coroutines(self.id)
        self.groups.clear()  # The groups have all completed now

        # 遍历执行 TestCollectionListener
        self.__notify_test_listeners_of_end(test_listener_searcher)

        # DEBUG时输出结果
        if log.level == logging.DEBUG:
            result_collector_searcher = SearchByClass(ResultCollector)
            self.tree.traverse(result_collector_searcher)
            result_collectors = result_collector_searcher.get_search_result()
            for result_collector in result_collectors:
                log.debug(f'resultCollector:\n{result_collector.__dict__}')

        # 测试结束
        self.active = False
        ContextService.end_test(self.id)  # todo 还要修改

    def stop_test(self):
        """停止所有 TestGroup（等待当前已启动的所有的 TestGroup 执行完成且不再执行剩余的 TestGroup）"""
        self.running = False
        for group in self.groups:
            group.stop_coroutines()

    def stop_test_now(self):
        """立即停止测试（强制中断所有的协程）"""
        self.running = False
        for group in self.groups:
            group.kill_groups()

    def __start_task_group(
        self,
        group: TestGroup,
        group_count: int,
        group_searcher: SearchByClass,
        collection_level_elements: list
    ) -> None:
        """启动TestGroup

        Args:
            group:                      TestGroup
            group_count:                TestGroup 总计（这里指序号，每启动一个 Gourp + 1）
            group_searcher:             SearchByClass[TestGroup]
            collection_level_elements:  TestCollection 子代节点（非 TestGroup 节点）

        Returns: None

        """
        try:
            number_groups = group.number_groups
            group_name = group.name

            # 把 TestCollection 子代节点（非 TestGroup 节点）添加至 TestGroup
            group_tree = group_searcher.get_subtree(group)
            group_tree.add_key_and_subkeys(group, collection_level_elements)
            log.info(f'TestGroup:[ {group_name} ] 启动 {number_groups} 个协程')

            # 存储当前 TestGroup，用于后续管理协程（启动、停止或循环）
            self.groups.append(group)
            group.start(group_count, group_tree, self)
        except StopTestException:
            log.error(traceback.format_exc())

    def __wait_groups_stopped(self) -> None:
        """等待所有协程执行完成"""
        for group in self.groups:
            group.wait_groups_stopped()

    @staticmethod
    def __notify_test_listeners_of_start(searcher: SearchByClass) -> None:
        """遍历调用 TestCollectionListener

        Args:
            searcher: SearchByClass[TestCollectionListener]

        Returns: None

        """
        log.debug('notify all TestCollectionListener to start')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_started()

    @staticmethod
    def __notify_test_listeners_of_end(searcher: SearchByClass) -> None:
        """遍历调用 TestCollectionListener

        Args:
            searcher: SearchByClass[TestCollectionListener]

        Returns: None

        """
        log.debug('notify all TestCollectionListener to end')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_ended()

    @staticmethod
    def __remove_groups(elements: list) -> None:
        """遍历删除 TestGroup 节点

        Args:
            elements: TestCollection 子代节点的列表

        Returns: None

        """
        for node in elements[:]:
            if isinstance(node, TestGroup) or not isinstance(node, TestElement):
                elements.remove(node)
