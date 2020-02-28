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
        pass

    def is_done(self):
        pass

    def initialize(self):
        pass

    def trigger_end_of_loop(self):
        pass
