#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import logging
from typing import Optional

from gevent import Greenlet
from loguru import logger

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
from pymeter.tools.exceptions import EngineException
from pymeter.tools.exceptions import StopTestException


class Properties(dict):

    def put(self, key: str, value: any) -> None:
        self[key] = value


class EngineContext:

    def __init__(self):
        self.test_start = 0
        self.number_of_active_coroutine = 0
        self.number_of_coroutines_started = 0
        self.number_of_coroutines_finished = 0
        self.total_threads = 0


class StandardEngine(Greenlet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.active = False
        self.tree = None
        self.serialized = True  # 标识 TestGroup 是否顺序运行
        self.groups = []  # 储存已启动的 TestGroup
        self.context: EngineContext = EngineContext()
        self.properties: Properties = Properties()
        self.collection: Optional[TestCollection] = None
        if props := getattr(kwargs, 'props', None):
            self.properties.update(props)

    def configure(self, tree: HashTree) -> None:
        """将脚本配置到执行引擎中"""
        # 查找脚本顶层列表中的 TestCollection 对象
        searcher = SearchByClass(TestCollection)
        tree.traverse(searcher)
        collections = searcher.get_search_result()

        if len(collections) == 0:
            raise EngineException('集合数量少于1，请确保至少存在一个集合')

        self.collection = collections[0]
        self.serialized = self.collection.serialized
        self.active = True
        self.tree = tree

    def run_test(self) -> None:
        """执行脚本，这里主要做异常捕获"""
        try:
            self.start()
            self.join()  # 等待主线程结束
        except EngineException:
            logger.exception()

    def _run(self, *args, **kwargs) -> None:
        """脚本执行主体"""
        logger.info('开始执行脚本')
        self.running = True

        ContextService.get_context().engine = self
        ContextService.start_test()

        # 查找 TestCollectionListener 对象
        test_listener_searcher = SearchByClass(TestCollectionListener)
        self.tree.traverse(test_listener_searcher)

        # 遍历执行 TestCollectionListener
        self.__notify_test_listeners_of_start__(test_listener_searcher)

        # 存储 TestCollection 子代节点(非 TestGroup 节点)
        collection_level_elements = self.tree.index(0).list()
        self.__remove_groups__(collection_level_elements)  # 删除 TestGroup 节点

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

        group_total = 0
        group_count = 0
        ContextService.clear_total_coroutines()

        # ####################################################################################################
        # SetUpGroup 运行主体
        # ####################################################################################################
        logger.info('开始处理 #前置线程组#')
        while self.running:
            try:
                setup_group: SetupGroup = next(setup_group_iter)
                group_count += 1
                group_name = setup_group.name
                logger.info(f'初始化第 {group_count} 个 #前置线程组# ，名称:[ {group_name} ]')
                self.__start_test_group__(setup_group, group_count, setup_group_searcher, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'等待当前 #前置线程组# 执行完成，名称:[ {group_name} ]')
                    setup_group.wait_groups_stopped()
            except StopIteration:
                logger.info('所有 #前置线程组# 已启动')
                break

        logger.info('等待所有 #前置线程组# 执行完成')
        self.__wait_groups_stopped__()
        logger.info('所有 #前置线程组# 执行完成')
        group_total += group_count
        group_count = 0
        ContextService.clear_total_coroutines()
        self.groups.clear()  # The groups have all completed now

        # ####################################################################################################
        # TestGroup 运行主体
        # ####################################################################################################
        logger.info(f'开始 #{"顺序" if self.serialized else "并行"}# 处理 #线程组#')
        while self.running:
            try:
                group: TestGroup = next(group_iter)
                if isinstance(group, (SetupGroup, TearDownGroup)):
                    continue
                group_count += 1
                group_name = group.name
                logger.info(f'初始化第 {group_count} 个 #线程组# ，名称:[ {group_name} ]')
                self.__start_test_group__(group, group_count, group_searcher, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'等待当前 #线程组# 执行完成，名称:[ {group_name} ]')
                    group.wait_groups_stopped()
            except StopIteration:
                logger.info('所有 #线程组# 已启动')
                break

        group_total = group_total + group_count
        if group_count > 0:
            if not self.running:
                logger.info('测试已停止，不再启动剩余的 #线程组# ')
            if not self.serialized:
                logger.info('等待所有 #线程组# 执行完成')

        logger.info('等待所有 #线程组# 执行完成')
        self.__wait_groups_stopped__()
        logger.info('所有 #线程组# 执行完成')
        group_count = 0
        ContextService.clear_total_coroutines()
        self.groups.clear()  # The groups have all completed now

        # ####################################################################################################
        # TeardownGroup 运行主体
        # ####################################################################################################
        logger.info('开始处理 #后置线程组#')
        while self.running:
            try:
                teardown_group: TearDownGroup = next(teardown_group_iter)
                group_count += 1
                group_name = teardown_group.name
                logger.info(f'初始化第 {group_count} 个 #后置线程组# ，名称:[ {group_name} ]')
                self.__start_test_group__(teardown_group, group_count, teardown_group_searcher, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'等待当前 #后置线程组# 完成，名称:[ {group_name} ]')
                    teardown_group.wait_groups_stopped()
            except StopIteration:
                logger.info('所有 #后置线程组# 已启动')
                break

        logger.info('等待所有 #后置线程组# 执行完成')
        self.__wait_groups_stopped__()
        logger.info('所有 #后置线程组# 执行完成')
        group_total = group_total + group_count
        ContextService.clear_total_coroutines()
        self.groups.clear()  # The groups have all completed now

        if group_total == 0:
            logger.warning('集合下找不到 #线程组# 或已被禁用')

        # 遍历执行 TestCollectionListener
        self.__notify_test_listeners_of_end__(test_listener_searcher)

        # DEBUG时输出结果
        if logger.level == logging.DEBUG:
            result_collector_searcher = SearchByClass(ResultCollector)
            self.tree.traverse(result_collector_searcher)
            result_collectors = result_collector_searcher.get_search_result()
            for result_collector in result_collectors:
                logger.debug(f'resultCollector:\n{result_collector.__dict__}')

        # 测试结束
        self.active = False
        ContextService.end_test()

    def stop_test(self):
        """停止所有 TestGroup（等待当前已启动的所有的 TestGroup 执行完成且不再执行剩余的 TestGroup）"""
        self.running = False
        for group in self.groups:
            group.stop_coroutines()

    def stop_test_now(self):
        """立即停止测试（强制中断所有的线程）"""
        self.running = False
        for group in self.groups:
            group.kill_groups()

    def __start_test_group__(
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
            logger.info(f'启动 #线程组# ，名称:[ {group_name} ]，线程数:[ {number_groups} ]')

            # 存储当前 TestGroup，用于后续管理线程（启动、停止或循环）
            self.groups.append(group)
            group.start(group_count, group_tree, self)
        except StopTestException:
            logger.exception()  # TODO: 这里需要打印堆栈吗

    def __wait_groups_stopped__(self) -> None:
        """等待所有线程执行完成"""
        for group in self.groups:
            group.wait_groups_stopped()

    @staticmethod
    def __notify_test_listeners_of_start__(searcher: SearchByClass) -> None:
        """遍历调用 TestCollectionListener

        Args:
            searcher: SearchByClass[TestCollectionListener]

        Returns: None

        """
        logger.debug('notify all TestCollectionListener to start')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_started()

    @staticmethod
    def __notify_test_listeners_of_end__(searcher: SearchByClass) -> None:
        """遍历调用 TestCollectionListener

        Args:
            searcher: SearchByClass[TestCollectionListener]

        Returns: None

        """
        logger.debug('notify all TestCollectionListener to end')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_ended()

    @staticmethod
    def __remove_groups__(elements: list) -> None:
        """遍历删除 TestGroup 节点

        Args:
            elements: TestCollection 子代节点的列表

        Returns: None

        """
        # 复制 elements 后遍历
        for node in elements[:]:
            if isinstance(node, TestGroup) or not isinstance(node, TestElement):
                elements.remove(node)
