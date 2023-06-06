#!/usr/bin python3
# @File    : worker.py
# @Time    : 2023-05-22 15:02:22
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique

from pymeter.controls.controller import Controller


@unique
class LogicalAction(Enum):
    """Sampler失败时，下一步动作的逻辑枚举"""

    # 错误时继续
    CONTINUE = 'continue'

    # 错误时开始下一个线程控制器的循环
    START_NEXT_ITERATION_OF_THREAD = 'start_next_thread'

    # 错误时开始下一个当前控制器（线程控制器或子代控制器）的循环
    START_NEXT_ITERATION_OF_CURRENT_LOOP = 'start_next_current_loop'

    # 错误时中断当前控制器的循环
    BREAK_CURRENT_LOOP = 'break_current_loop'

    # 错误时停止线程
    STOP_WORKER = 'stop_worker'

    # 错误时停止测试执行
    STOP_TEST = 'stop_test'

    # 错误时立即停止测试执行（中断线程）
    STOP_NOW = 'stop_now'


class Worker(Controller):

    # 运行策略
    RUNNING_STRATEGY = 'Worker__running_strategy'

    @property
    def running_strategy(self):
        return self.get_property(self.RUNNING_STRATEGY).get_obj()
