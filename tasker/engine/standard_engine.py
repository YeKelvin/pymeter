#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import logging
import traceback

from gevent import Greenlet

from tasker.common.exceptions import EngineException
from tasker.common.exceptions import StopTestException
from tasker.elements.element import TaskElement
from tasker.engine.collection import TaskCollection
from tasker.engine.interface import TaskCollectionListener
from tasker.engine.traverser import SearchByClass
from tasker.engine.tree import HashTree
from tasker.groups.context import ContextService
from tasker.groups.group import TaskGroup
from tasker.listeners.result_collector import ResultCollector
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class StandardEngine(Greenlet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = None
        self.running = False
        self.active = False
        self.tree = None
        self.serialized = True  # 标识TaskGroup是否顺序运行
        self.groups = []  # 储存已启动的TaskGroup

    def configure(self, tree: HashTree) -> None:
        """将脚本配置到执行引擎中
        """
        # 查找脚本顶层列表中的TaskCollection对象
        searcher = SearchByClass(TaskCollection)
        tree.traverse(searcher)
        collections = searcher.get_search_result()

        if len(collections) == 0:
            raise EngineException('TaskCollection数量少于1，请确保至少存在一个TaskCollection')

        self.serialized = collections[0].serialized
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

        # 查找TaskCollectionListener对象
        test_listener_searcher = SearchByClass(TaskCollectionListener)
        self.tree.traverse(test_listener_searcher)

        # 遍历执行TaskCollectionListener
        self.__notify_test_listeners_of_start(test_listener_searcher)

        # 存储collection层一级子代的节点(非TaskGroup节点)
        collection_level_elements = self.tree.index(0).list()
        self.__remove_coroutine_groups(collection_level_elements)  # 删除 TaskGroup节点

        # 查找TaskGroup对象
        group_searcher = SearchByClass(TaskGroup)
        self.tree.traverse(group_searcher)
        group_iter = iter(group_searcher.get_search_result())

        group_count = 0
        ContextService.clear_total_coroutines(self.id)  # TODO: 还要修改

        log.info(f'开始执行TaskGroup，执行方式:[ {"顺序" if self.serialized else "并行"}执行 ]')
        while self.running:
            try:
                group: TaskGroup = next(group_iter)
                group_count += 1
                group_name = group.name
                log.info(f'开始第 {group_count} 个TaskGroup，Task名称:[ {group_name} ]')
                self.__start_task_group(group, group_count, group_searcher, collection_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    log.info(f'开始下一个TaskGroup之前等待上一个TaskGroup完成，上一个Task名称:[ {group_name} ]')
                    group.wait_groups_stopped()
            except StopIteration:
                log.info('所有TaskGroup已启动')
                break

        if group_count == 0:
            log.warning('TaskCollection下找不到已启用的TaskGroup或所有TaskGroup已被禁用')
        else:
            if not self.running:
                log.info('Task已停止，不再启动剩余的TaskGroup')
            if not self.serialized:
                log.info('等待所有TaskGroup执行完成')
                self.__wait_groups_stopped()

            log.info('TaskCollection下的所有TaskGroup已执行完成')
            self.groups.clear()

            # 遍历执行TaskCollectionListener
            self.__notify_test_listeners_of_end(test_listener_searcher)

        # debug打印结果
        if log.level == logging.DEBUG:
            result_collector_searcher = SearchByClass(ResultCollector)
            self.tree.traverse(result_collector_searcher)
            result_collectors = result_collector_searcher.get_search_result()
            for result_collector in result_collectors:
                log.debug(f'result_collector:\n{result_collector.__dict__}')

        # Task结束
        self.active = False
        ContextService.end_test(self.id)  # todo 还要修改

    def stop_test(self):
        """停止所有TaskGroup（等待当前已启动的所有的TaskGroup执行完成且不再执行剩余的TaskGroup）
        """
        self.running = False
        for group in self.groups:
            group.stop_coroutines()

    def stop_test_now(self):
        """立即停止Task（强制中断所有的协程）
        """
        self.running = False
        for group in self.groups:
            group.kill_groups()

    def __start_task_group(
        self,
        group: TaskGroup,
        group_count: int,
        group_searcher: SearchByClass,
        collection_level_elements: list
    ) -> None:
        """启动TaskGroup

        Args:
            group:                      TaskGroup对象
            group_count:                group的总数（这里指序号，每启动一个 Gourp+1）
            group_searcher:             SearchByClass(TaskGroup)对象
            collection_level_elements:  collection层一级子代的节点（非TaskGroup节点）

        Returns: None

        """
        try:
            number_groups = group.number_groups
            group_name = group.name

            # 把collection层一级子代的节点（非TaskGroup节点）添加至 group层
            group_tree = group_searcher.get_subtree(group)
            group_tree.add_key_and_subkeys(group, collection_level_elements)
            log.info(f'TaskGroup {group_name} 启动 {number_groups} 个协程')

            # 存储当前TaskGroup，用于后续管理协程（启动、停止或循环）
            self.groups.append(group)
            group.start(group_count, group_tree, self)
        except StopTestException:
            log.error(traceback.format_exc())

    def __wait_groups_stopped(self) -> None:
        """等待所有协程执行完成
        """
        for group in self.groups:
            group.wait_groups_stopped()

    @staticmethod
    def __notify_test_listeners_of_start(searcher: SearchByClass) -> None:
        """遍历调用 TaskCollectionListener

        Args:
            searcher: SearchByClass(TaskCollectionListener)对象

        Returns: None

        """
        log.debug('notify all TaskCollectionListener to start')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_started()

    @staticmethod
    def __notify_test_listeners_of_end(searcher: SearchByClass) -> None:
        """遍历调用 TaskCollectionListener

        Args:
            searcher: SearchByClass(TaskCollectionListener)对象

        Returns: None

        """
        log.debug('notify all TaskCollectionListener to end')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_ended()

    @staticmethod
    def __remove_coroutine_groups(elements: list) -> None:
        """遍历删除TaskGroup节点

        Args:
            elements: collection层一级子代节点的列表

        Returns: None

        """
        for node in elements[:]:
            if isinstance(node, TaskGroup) or not isinstance(node, TaskElement):
                elements.remove(node)
