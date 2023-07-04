#!/usr/bin python3
# @File    : context.py
# @Time    : 2023-07-04 16:27:08
# @Author  : Kelvin.Ye


class EngineContext:

    def __init__(self):
        self.test_start = 0
        self.total_threads = 0
        self.number_of_threads_actived = 0
        self.number_of_threads_started = 0
        self.number_of_threads_finished = 0
