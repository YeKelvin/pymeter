#!/usr/bin python3
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import logging
from typing import List

from gevent import Greenlet
from loguru import logger
from loguru._logger import context as logurucontext

from pymeter.collections.collection import TestCollection
from pymeter.elements.element import TestElement
from pymeter.engine.hashtree import HashTree
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.traverser import SearchByClass
from pymeter.listeners.result_collector import ResultCollector
from pymeter.tools.exceptions import EngineException
from pymeter.tools.exceptions import StopTestException
from pymeter.workers.context import ContextService
from pymeter.workers.setup_worker import SetupWorker
from pymeter.workers.teardown_worker import TearDownWorker
from pymeter.workers.test_worker import TestWorker


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
        self.collection = None
        self.serialized = True          # 是否顺序运行
        self.workers = []               # 储存已启动的worker
        self.context = EngineContext()
        self.properties = Properties()
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

        # 存储 TestCollection 子代节点(非 TestWorker 节点)
        collection_component_list = self.tree.index(0).list()
        self._remove_workers(collection_component_list)  # 删除 TestWorker 节点
        self._add_level(collection_component_list)       # 添加层级

        # 查找 SetupWorker / TestWorker / TearDownWorker 对象
        setup_worker_searcher = SearchByClass(SetupWorker)
        test_worker_searcher = SearchByClass(TestWorker)
        teardown_worker_searcher = SearchByClass(TearDownWorker)

        # 遍历查找
        self.tree.traverse(setup_worker_searcher)
        self.tree.traverse(test_worker_searcher)
        self.tree.traverse(teardown_worker_searcher)

        ContextService.clear_total_threads()
        worker_total = 0

        # 运行SetUpWorker
        worker_total += self._process_setup_worker(setup_worker_searcher, collection_component_list)
        # 运行TestWorker
        worker_total += self._process_test_worker(test_worker_searcher, collection_component_list)
        # 运行TeardownWorker
        worker_total += self._process_teardown_worker(teardown_worker_searcher, collection_component_list)

        if worker_total == 0:
            logger.warning('集合不存在 #工作者# 或已禁用')

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

    def _process_setup_worker(self, setup_worker_searcher, collection_component_list):
        if not setup_worker_searcher.count:
            return 0

        logger.info('开始处理 #前置工作者#')
        worker_count = 0
        setup_worker_iter = iter(setup_worker_searcher.get_search_result())
        while self.running:
            try:
                setup_worker: SetupWorker = next(setup_worker_iter)
                worker_count += 1
                worker_name = setup_worker.name
                logger.info(f'工作者:[ {worker_name} ] 初始化第 {worker_count} 个 #前置工作者#')
                self._start_worker(setup_worker, worker_count, setup_worker_searcher, collection_component_list)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'工作者:[ {worker_name} ] 等待当前 #前置工作者# 执行完成')
                    setup_worker.wait_workers_stopped()
            except StopIteration:
                logger.info('所有 #前置工作者# 已启动')
                break

        logger.info('等待所有 #前置工作者# 执行完成')
        self._wait_workers_stopped()
        self.workers.clear()  # The workers have all completed now
        ContextService.clear_total_threads()
        logger.info('所有 #前置工作者# 已执行完成')
        return worker_count

    def _process_test_worker(self, test_worker_searcher, collection_component_list):
        if not test_worker_searcher.count:
            return 0

        logger.info(f'开始 #{"串行" if self.serialized else "并行"}# 处理 #工作者#')
        worker_count = 0
        test_worker_iter = iter(test_worker_searcher.get_search_result())
        while self.running:
            try:
                test_worker: TestWorker = next(test_worker_iter)
                if isinstance(test_worker, (SetupWorker, TearDownWorker)):
                    continue
                worker_count += 1
                worker_name = test_worker.name
                logger.info(f'工作者:[ {worker_name} ] 初始化第 {worker_count} 个 #工作者#')
                self._start_worker(test_worker, worker_count, test_worker_searcher, collection_component_list)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'工作者:[ {worker_name} ] 等待当前 #工作者# 执行完成')
                    test_worker.wait_workers_stopped()
            except StopIteration:
                logger.info('所有 #工作者# 已启动')
                break

        if worker_count > 0:
            if not self.running:
                logger.info('测试已停止，不再启动剩余的 #工作者# ')
            if not self.serialized:
                logger.info('等待所有 #工作者# 执行完成')

        logger.info('等待所有 #工作者# 执行完成')
        self._wait_workers_stopped()
        self.workers.clear()  # The workers have all completed now
        ContextService.clear_total_threads()
        logger.info('所有 #工作者# 已执行完成')
        return worker_count

    def _process_teardown_worker(self, teardown_worker_searcher, collection_component_list):
        if not teardown_worker_searcher.count:
            return 0

        logger.info('开始处理 #后置工作者#')
        worker_count = 0
        teardown_worker_iter = iter(teardown_worker_searcher.get_search_result())
        while self.running:
            try:
                teardown_worker: TearDownWorker = next(teardown_worker_iter)
                worker_count += 1
                worker_name = teardown_worker.name
                logger.info(f'工作者:[ {worker_name} ] 初始化第 {worker_count} 个 #后置工作者#')
                self._start_worker(teardown_worker, worker_count, teardown_worker_searcher, collection_component_list)

                # 需要顺序执行时，则等待当前线程执行完毕再继续下一个循环
                if self.serialized:
                    logger.info(f'工作者:[ {worker_name} ] 等待当前 #后置工作者# 完成')
                    teardown_worker.wait_workers_stopped()
            except StopIteration:
                logger.info('所有 #后置工作者# 已启动')
                break

        logger.info('等待所有 #后置工作者# 执行完成')
        self._wait_workers_stopped()
        self.workers.clear()  # The workers have all completed now
        ContextService.clear_total_threads()
        logger.info('所有 #后置工作者# 已执行完成')
        return worker_count

    def stop_test(self):
        """停止所有 TestWorker（等待当前已启动的所有的 TestWorker 执行完成且不再执行剩余的 TestWorker）"""
        self.running = False
        for worker in self.workers:
            worker.stop_threads()

    def stop_test_now(self):
        """立即停止测试（强制中断所有的线程）"""
        self.running = False
        for worker in self.workers:
            worker.kill_workers()

    def _start_worker(
        self,
        worker: TestWorker,
        worker_count: int,
        worker_searcher: SearchByClass,
        collection_component_list: list
    ) -> None:
        """启动TestWorker

        Args:
            worker:                      TestWorker
            worker_count:                TestWorker 总计（这里指序号，每启动一个 Gourp + 1）
            worker_searcher:             SearchByClass[TestWorker]
            collection_component_list:   TestCollection 子代节点（非 TestWorker 节点）

        Returns:
            None

        """
        try:
            number_of_threads = worker.number_of_threads
            worker_name = worker.name

            # 将 Collection 层的组件节点（非 TestWorker 节点）添加至 TestWorker
            worker_tree = worker_searcher.get(worker)
            worker_tree.add_key(worker).add_keys(collection_component_list)
            logger.info(f'工作者:[ {worker_name} ] 线程数:[ {number_of_threads} ] 启动 #工作者#')

            # 存储当前 TestWorker，用于后续管理线程（启动、停止或循环）
            self.workers.append(worker)
            worker.start(worker_count, worker_tree, self)
        except StopTestException:
            logger.info('停止运行')

    def _wait_workers_stopped(self) -> None:
        """等待所有线程执行完成"""
        for worker in self.workers:
            worker.wait_workers_stopped()

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
    def _remove_workers(elements: list) -> None:
        """遍历删除 TestWorker 节点

        Args:
            elements: TestCollection 子代节点的列表

        Returns: None

        """
        # 复制 elements 后遍历
        for node in elements[:]:
            if isinstance(node, TestWorker) or not isinstance(node, TestElement):
                elements.remove(node)

    @staticmethod
    def _add_level(elements: List[TestElement]) -> None:
        for node in elements:
            if node.level is None:
                node.level = 1
