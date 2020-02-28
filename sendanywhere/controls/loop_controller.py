#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : loop_controller
# @Time    : 2020/2/28 17:16
# @Author  : Kelvin.Ye
from sendanywhere.controls.generic_controller import GenericController
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class LoopController(GenericController):
    def __init__(self, loops: int, continue_forever: bool):
        super().__init__()
        self.loops = loops
        self.continue_forever = continue_forever
        self.loopCount = 0

    def next(self) -> Sampler:
        self.update_iteration_index()

    def is_done(self):
        pass

    def initialize(self):
        pass

    def trigger_end_of_loop(self):
        pass

    def update_iteration_index(self):
        pass

    def end_of_loop(self):
        pass

    def next_is_null(self):
        pass

    def increment_loop_count(self):
        pass

    def reset_loop_count(self):
        pass

    def re_initialize(self):
        pass

    def start_next_loop(self):
        pass

    def reset_break_loop(self):
        pass

    def break_loop(self):
        pass

    def iteration_start(self):
        pass
