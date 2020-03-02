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
        self.serialized = True  # 标识协程组是否顺序运行
        self.groups = []  # 储存已启动的 CoroutineGroup

    def configure(self, tree: HashTree) -> None:
        """将脚本配置到执行引擎中
        """
        # 查找 CoroutineCollection脚本顶层集合对象
        searcher = SearchByClass(CoroutineCollection)
        tree.traverse(searcher)
        collections = searcher.get_search_result()

        if len(collections) == 0:
            raise EngineException('脚本集合数量少于1，请确保至少存在一个脚本集合')

        self.serialized = collections[0].serialized
        self.active = True
        self.tree = tree

    def run_test(self) -> None:
        """执行脚本，这里主要做异常捕获
        """
        try:
            self.run()
        except EngineException:
            log.error(traceback.format_exc())

    def run(self) -> None:
        """脚本执行主体
        """
        log.info('开始执行脚本')
        self.running = True

        # 查找 TestStateListener对象
        test_listener_searcher = SearchByClass(TestStateListener)
        self.tree.traverse(test_listener_searcher)

        # 遍历执行 TestStateListener.test_started()
        self.__notify_test_listeners_of_start(test_listener_searcher)

        # 储存 collection层的非 CoroutineGroup节点
        test_level_elements = self.tree.index(0).list()
        self.__remove_coroutine_groups(test_level_elements)  # 删除 CoroutineGroup节点

        # 查找 CoroutineGroup对象
        group_searcher = SearchByClass(CoroutineGroup)
        self.tree.traverse(group_searcher)
        group_iter = iter(group_searcher.get_search_result())

        group_count = 0
        ContextService.clear_total_threads()  # todo 还要修改

        if self.serialized:
            log.info('开始顺序执行协程组')
        else:
            log.info('开始并行执行协程组')

        while self.running:
            try:
                group: CoroutineGroup = next(group_iter)
                group_count += 1
                group_name = group.name
                log.info(f'开始第 [{group_count}] 个协程组: [{group_name}]')
                self.__start_coroutine_group(group, group_count, group_searcher, test_level_elements)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    log.info(f'在开始下一个协程组之前等待 [{group_name}] 协程组完成')
                    group.wait_coroutines_stopped()
            except StopIteration:
                log.info('所有协程组已启动')
                break

        if group_count == 0:
            log.info('脚本集合下找不到可用的协程组')
        else:
            if not self.running:
                log.info('测试已停止，不再启动协程组')
            if not self.serialized:
                log.info('等待所有协程组执行完成')
                self.__wait_coroutines_stopped()

            log.info('脚本集合下的所有协程组已经执行完成')
            self.groups.clear()

            # 遍历执行 TestStateListener.test_ended()
            self.__notify_test_listeners_of_end(test_listener_searcher)

        # 测试结束
        ContextService.end_test()  # todo 还要修改

    def stop_test_now(self):
        """立即停止测试
        """
        for group in self.groups:
            group.tell_coroutines_to_stop()

    def stop_all_coroutines(self):
        """停止所有协程组
        """
        for group in self.groups:
            group.stop()

    def __start_coroutine_group(self,
                                group: CoroutineGroup,
                                group_count: int,
                                group_searcher: SearchByClass,
                                test_level_elements: list) -> None:
        """启动协程组
        """
        try:
            number_coroutines = group.number_coroutines
            group_name = group.name
            group_tree = group_searcher.get_subtree(group)
            group_tree.put_all(group, test_level_elements)  # 把 collection层的非 group节点添加至 group层的 hashtree
            log.info(f'为 [{group_name}] 协程组启动 [{number_coroutines}] 个协程')

            self.groups.append(group)  # 存储当前协程组，用于停止协程
            group.start(group_count, group_tree, self)
        except StopTestException:
            log.error(traceback.format_exc())

    def __wait_coroutines_stopped(self) -> None:
        """等待所有协程执行完成
        """
        for group in self.groups:
            group.wait_coroutines_stopped()

    @staticmethod
    def __notify_test_listeners_of_start(searcher: SearchByClass) -> None:
        """遍历调用 TestStateListener.test_start()
        """
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.test_started()

    @staticmethod
    def __notify_test_listeners_of_end(searcher: SearchByClass) -> None:
        """遍历调用 TestStateListener.test_ended()
        """
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.test_ended()

    @staticmethod
    def __remove_coroutine_groups(elements: list) -> None:
        """遍历删除 CoroutineGroup节点
        """
        for node in elements[:]:
            if isinstance(node, CoroutineGroup) or not isinstance(node, TestElement):
                elements.remove(node)
