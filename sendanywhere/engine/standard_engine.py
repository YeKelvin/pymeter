#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : standard_engine
# @Time    : 2020/1/24 23:31
# @Author  : Kelvin.Ye
import traceback

from sendanywhere.engine.exceptions import SenderEngineException
from sendanywhere.threads.context import SenderContextService
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class StandardSenderEngine:
    def __init__(self):
        self.running = False
        self.active = False
        self.tree = None
        self.serialized = True  # 线程组是否按顺序运行

    def configure(self, tree):
        self.tree = tree
        self.active = True
        # 设置线程组是否按顺序运行
        # self.serialized =

    def run_test(self):
        try:
            self.run()
        except SenderEngineException:
            log.error(traceback.format_exc())

    def run(self):
        log.info('Running the test!')
        self.running = True

        # test_listeners = SearchByClass<TestStateListener>
        # 遍历执行 TestStateListener.testStarted()
        # self.notify_test_listeners_of_start(test_listeners)

        # group_searcher = SearchByClass<ThreadGroup>
        # group_iter = group_searcher.getSearchResults().iterator()

        group_count = 0
        SenderContextService.clear_total_threads()

        while self.running and group_iter.hasNext():
            group = group_iter.next()
            group_count += 1

            group_name = group.name
            log.info(f'Starting ThreadGroup: {group_count} : {group_name}')
            self.start_thread_group(group, group_count, group_searcher)

            if self.serialized and group_iter.hasNext():
                log.info(f'Waiting for thread group: {group_name} to finish before starting next group')
                group.wait_threads_stopped()
        #  end of thread groups

        if group_count == 0:  # No thread groups found
            log.info("No enabled thread groups found")
        else:
            if self.running:
                log.info('All thread groups have been started')
            else:
                log.info('Test stopped - no more thread groups will be started')

        # wait for all Test Threads To Exit
        self.wait_threads_stopped()

        # 遍历执行 TestStateListener.testEnded()
        # notify_test_listeners_of_end(test_listeners);

        # 测试结束
        SenderContextService.end_test()
