#!/usr/bin python3
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import logging

from gevent import Greenlet
from loguru import logger
from loguru._logger import context as logurucontext

from pymeter.collections.collection import TestCollection
from pymeter.elements.element import TestElement
from pymeter.engine.hashtree import HashTree
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.traverser import SearchByClass
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
        self.number_of_threads_actived = 0
        self.number_of_threads_started = 0
        self.number_of_threads_finished = 0
        self.total_threads = 0


class StandardEngine(Greenlet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.active = False
        self.tree = None
        self.serialized = True          # 是否顺序运行
        self.groups = []                # 储存已启动的worker
        self.context = EngineContext()
        self.properties = Properties()
        self.collection = None
        self.extra = kwargs.get('extra', {})
        self.properties.update(kwargs.get('props', {}))

    def configure(self, tree: HashTree) -> None:
        """将脚本配置到执行引擎中"""
        # 查找脚本顶层列表中的 TestCollection 对象
        searcher = SearchByClass(TestCollection)
        tree.traverse(searcher)
        collections = searcher.get_search_result()

        if len(collections) == 0:
            raise EngineException('集合不允许为空')

        self.collection: TestCollection = collections[0]
        self.serialized = self.collection.serialized
        self.active = True
        self.tree = tree

    def run_test(self) -> None:
        """运行脚本，这里主要做异常捕获"""
        try:
            self.start()  # _run()
            self.join()  # 等待主线程结束
        except EngineException as e:
            logger.error(e)
        except Exception:
            logger.exception('Exception Occurred')

    def _run(self, *args, **kwargs) -> None:
        """脚本运行主体"""
        logger.info('开始运行脚本')

        # log注入traceid和sid
        logurucontext.set({
            **logurucontext.get(),
            'traceid': self.extra.get('traceid'),
            'sid': self.extra.get('sid')
        })

        # 标记运行状态
        self.running = True

        # 上下文存储引擎和全局变量
        ctx = ContextService.get_context()
        ctx.engine = self
        ctx.variables.update(self.properties)
        # 上下文标记开始运行
        ContextService.start_test()

        # 查找 TestCollectionListener 对象
        collection_listener_searcher = SearchByClass(TestCollectionListener)
        self.tree.traverse(collection_listener_searcher)

        # 遍历执行 TestCollectionListener
        self._notify_collection_listeners_of_start(collection_listener_searcher)

        # 存储 TestCollection 子代节点(非 TestGroup 节点)
        collection_component_list = self.tree.index(0).list()
        self._remove_groups(collection_component_list)  # 删除 TestGroup 节点
        self._add_level(collection_component_list)      # 添加层级

        # 查找 SetupGroup / TestGroup / TearDownGroup 对象
        setup_group_searcher = SearchByClass(SetupGroup)
        test_group_searcher = SearchByClass(TestGroup)
        teardown_group_searcher = SearchByClass(TearDownGroup)

        # 遍历查找
        self.tree.traverse(setup_group_searcher)
        self.tree.traverse(test_group_searcher)
        self.tree.traverse(teardown_group_searcher)

        ContextService.clear_total_threads()
        group_total = 0

        # 运行SetUpGroup
        group_total += self._process_setup_group(setup_group_searcher, collection_component_list)
        # 运行TestGroup
        group_total += self._process_test_group(test_group_searcher, collection_component_list)
        # 运行TeardownGroup
        group_total += self._process_teardown_group(teardown_group_searcher, collection_component_list)

        if group_total == 0:
            logger.warning('集合不存在 #线程组# 或已禁用')

        # 遍历执行 TestCollectionListener
        self._notify_collection_listeners_of_end(collection_listener_searcher)

        # DEBUG时输出结果
        if logger.level == logging.DEBUG:
            result_collector_searcher = SearchByClass(ResultCollector)
            self.tree.traverse(result_collector_searcher)
            result_collectors = result_collector_searcher.get_search_result()
            for result_collector in result_collectors:
                logger.debug(f'取样结果:\n{result_collector.__dict__}')

        # 测试结束
        self.active = False
        ContextService.end_test()
        logger.info('脚本运行完成')

    def _process_setup_group(self, setup_group_searcher, collection_component_list):
        if not setup_group_searcher.count:
            return 0

        logger.info('开始处理 #前置线程组#')
        group_count = 0
        setup_group_iter = iter(setup_group_searcher.get_search_result())
        while self.running:
            try:
                setup_group: SetupGroup = next(setup_group_iter)
                group_count += 1
                group_name = setup_group.name
                logger.info(f'名称:[ {group_name} ] 初始化第 {group_count} 个 #前置线程组#')
                self._start_test_group(setup_group, group_count, setup_group_searcher, collection_component_list)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'名称:[ {group_name} ] 等待当前 #前置线程组# 执行完成')
                    setup_group.wait_groups_stopped()
            except StopIteration:
                logger.info('所有 #前置线程组# 已启动')
                break

        logger.info('等待所有 #前置线程组# 执行完成')
        self._wait_groups_stopped()
        self.groups.clear()  # The groups have all completed now
        ContextService.clear_total_threads()
        logger.info('所有 #前置线程组# 已执行完成')
        return group_count

    def _process_test_group(self, test_group_searcher, collection_component_list):
        if not test_group_searcher.count:
            return 0

        logger.info(f'开始 #{"顺序" if self.serialized else "并行"}# 处理 #线程组#')
        group_count = 0
        test_group_iter = iter(test_group_searcher.get_search_result())
        while self.running:
            try:
                test_group: TestGroup = next(test_group_iter)
                if isinstance(test_group, (SetupGroup, TearDownGroup)):
                    continue
                group_count += 1
                group_name = test_group.name
                logger.info(f'名称:[ {group_name} ] 初始化第 {group_count} 个 #线程组#')
                self._start_test_group(test_group, group_count, test_group_searcher, collection_component_list)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'名称:[ {group_name} ] 等待当前 #线程组# 执行完成')
                    test_group.wait_groups_stopped()
            except StopIteration:
                logger.info('所有 #线程组# 已启动')
                break

        if group_count > 0:
            if not self.running:
                logger.info('测试已停止，不再启动剩余的 #线程组# ')
            if not self.serialized:
                logger.info('等待所有 #线程组# 执行完成')

        logger.info('等待所有 #线程组# 执行完成')
        self._wait_groups_stopped()
        self.groups.clear()  # The groups have all completed now
        ContextService.clear_total_threads()
        logger.info('所有 #线程组# 已执行完成')
        return group_count

    def _process_teardown_group(self, teardown_group_searcher, collection_component_list):
        if not teardown_group_searcher.count:
            return 0

        logger.info('开始处理 #后置线程组#')
        group_count = 0
        teardown_group_iter = iter(teardown_group_searcher.get_search_result())
        while self.running:
            try:
                teardown_group: TearDownGroup = next(teardown_group_iter)
                group_count += 1
                group_name = teardown_group.name
                logger.info(f'名称:[ {group_name} ] 初始化第 {group_count} 个 #后置线程组#')
                self._start_test_group(teardown_group, group_count, teardown_group_searcher, collection_component_list)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'名称:[ {group_name} ] 等待当前 #后置线程组# 完成')
                    teardown_group.wait_groups_stopped()
            except StopIteration:
                logger.info('所有 #后置线程组# 已启动')
                break

        logger.info('等待所有 #后置线程组# 执行完成')
        self._wait_groups_stopped()
        self.groups.clear()  # The groups have all completed now
        ContextService.clear_total_threads()
        logger.info('所有 #后置线程组# 已执行完成')
        return group_count

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

    def _start_test_group(
        self,
        group: TestGroup,
        group_count: int,
        group_searcher: SearchByClass,
        collection_component_list: list
    ) -> None:
        """启动TestGroup

        Args:
            group:                      TestGroup
            group_count:                TestGroup 总计（这里指序号，每启动一个 Gourp + 1）
            group_searcher:             SearchByClass[TestGroup]
            collection_component_list:  TestCollection 子代节点（非 TestGroup 节点）

        Returns:
            None

        """
        try:
            number_groups = group.number_groups
            group_name = group.name

            # 将 Collection 层的组件节点（非 TestGroup 节点）添加至 TestGroup
            group_tree = group_searcher.get(group)
            group_tree.add_key(group).add_keys(collection_component_list)
            logger.info(f'名称:[ {group_name} ] 线程数:[ {number_groups} ] 启动 #线程组#')

            # 存储当前 TestGroup，用于后续管理线程（启动、停止或循环）
            self.groups.append(group)
            group.start(group_count, group_tree, self)
        except StopTestException:
            logger.info('停止运行')

    def _wait_groups_stopped(self) -> None:
        """等待所有线程执行完成"""
        for group in self.groups:
            group.wait_groups_stopped()

    @staticmethod
    def _notify_collection_listeners_of_start(searcher: SearchByClass) -> None:
        """遍历调用 TestCollectionListener

        Args:
            searcher: SearchByClass[TestCollectionListener]

        Returns: None

        """
        logger.debug('遍历触发 TestCollectionListener 的开始事件')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_started()

    @staticmethod
    def _notify_collection_listeners_of_end(searcher: SearchByClass) -> None:
        """遍历调用 TestCollectionListener

        Args:
            searcher: SearchByClass[TestCollectionListener]

        Returns: None

        """
        logger.debug('遍历触发 TestCollectionListener 的结束事件')
        listeners = searcher.get_search_result()
        for listener in listeners:
            listener.collection_ended()

    @staticmethod
    def _remove_groups(elements: list) -> None:
        """遍历删除 TestGroup 节点

        Args:
            elements: TestCollection 子代节点的列表

        Returns: None

        """
        # 复制 elements 后遍历
        for node in elements[:]:
            if isinstance(node, TestGroup) or not isinstance(node, TestElement):
                elements.remove(node)

    @staticmethod
    def _add_level(elements: list) -> None:
        for node in elements:
            if node.level is None:
                node.level = 1
