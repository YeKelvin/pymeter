#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import traceback

from gevent import Greenlet

from sendanywhere.coroutines.collection import CoroutineCollection
from sendanywhere.coroutines.context import ContextService
from sendanywhere.coroutines.group import CoroutineGroup
from sendanywhere.engine.collection.traverser import SearchByClass
from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.engine.exceptions import EngineException, StopTestException
from sendanywhere.engine.listener import TestStateListener
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class StandardEngine(Greenlet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.active = False
        self.tree = None
        self.serialized = True  # 线程组是否按顺序运行
        self.groups = []

    def configure(self, tree: HashTree):
        searcher = SearchByClass(CoroutineCollection)
        tree.traverse(searcher)
        collections = searcher.get_search_result()
        if len(collections) == 0:
            raise EngineException('脚本集合数量少于1，请确保至少存在一个脚本集合')

        self.serialized = collections[0].serialized  # 线程组是否按顺序运行
        self.active = True
        self.tree = tree

    def run_test(self):
        try:
            self.run()
        except EngineException:
            log.error(traceback.format_exc())

    def run(self):
        log.info('Running the test!')
        self.running = True

        # 查找 TestStateListener对象
        test_listener_searcher = SearchByClass(TestStateListener)
        self.tree.traverse(test_listener_searcher)
        # 遍历执行 TestStateListener.test_started()
        self.__notify_test_listeners_of_start(test_listener_searcher)

        # 储存 CoroutineCollection层的非 CoroutineGroup节点和 非 TestElement节点
        test_level_elements = self.tree.get(self.tree.list()[0]).list()
        self.__remove_coroutine_groups(test_level_elements)

        # 查找 CoroutineGroup对象
        group_searcher = SearchByClass(CoroutineGroup)
        self.tree.traverse(group_searcher)
        group_iter = iter(group_searcher.get_search_result())

        group_count = 0
        ContextService.clear_total_threads()

        while self.running:
            try:
                group: CoroutineGroup = next(group_iter)
                group_count += 1
                group_name = group.name
                log.info(f'Starting coroutine group: {group_count} : {group_name}')
                self.__start_coroutine_group(group, group_count, group_searcher, test_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    log.info(f'Waiting for coroutine group: {group_name} to finish before starting next group')
                    group.wait_coroutines_stopped()
            except StopIteration:
                break
        #  end of coroutine groups

        if group_count == 0:  # No coroutine groups found
            log.info('No enabled coroutine groups found')
        else:
            if self.running:
                log.info('All coroutine groups have been started')
            else:
                log.info('Test stopped - no more coroutine groups will be started')

        if not self.serialized:
            # wait for all test coroutines to exit
            self.__wait_coroutines_stopped()

        self.groups.clear()

        # 遍历执行 TestStateListener.test_ended()
        self.__notify_test_listeners_of_end(test_listener_searcher)

        # 测试结束
        ContextService.end_test()

    def __start_coroutine_group(self,
                              group: CoroutineGroup,
                              group_count: int,
                              group_searcher: SearchByClass,
                              test_level_elements: list):
        try:
            number_coroutines = group.number_coroutines
            group_name = group.name
            group_tree = group_searcher.get_subtree(group)
            group_tree.put(group, test_level_elements)  # todo 添加父级非 group节点
            log.info(f'Starting {number_coroutines} coroutines for group {group_name}.')
            self.groups.append(group)
            group.start(group_count, group_tree, self)
        except StopTestException:
            log.error(traceback.format_exc())

    def __wait_coroutines_stopped(self):
        """等待所有协程执行完成
        """
        for group in self.groups:
            group.wait_coroutines_stopped()

    @staticmethod
    def __notify_test_listeners_of_start(searcher: SearchByClass) -> None:
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.test_started()

    @staticmethod
    def __notify_test_listeners_of_end(searcher: SearchByClass) -> None:
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.test_ended()

    @staticmethod
    def __remove_coroutine_groups(elements: list):
        for node in elements[:]:
            if isinstance(node, CoroutineGroup) or not isinstance(node, TestElement):
                elements.remove(node)
