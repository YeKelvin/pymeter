#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : while_controller.py
# @Time    : 2021-08-26 18:08:15
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.controls.controller import IteratingController
from pymeter.controls.generic_controller import GenericController
from pymeter.groups.group import Coroutine
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class WhileController(GenericController, IteratingController):

    CONDITION: Final = 'WhileController__condition'

    @property
    def condition(self) -> str:
        return self.get_property_as_str(self.CONDITION)

    @property
    def last_sample_ok(self) -> str:
        return self.ctx.variables.get(Coroutine.LAST_SAMPLE_OK)

    def __init__(self):
        super().__init__()
        self.break_loop = False

    # Evaluate the condition, which can be:
    # blank or LAST = was the last sampler OK?
    # otherwise, evaluate the condition to see if it is not "false"
    # If blank, only evaluate at the end of the loop
    # Must only be called at start and end of loop
    def end_of_loop(self, loop_end: bool):
        if self.break_loop:
            return True

        cnd = self.condition.strip()
        log.debug(f'while condition:[ {cnd} ]')
        result = False

        # If blank, only check previous sample when at end of loop
        if loop_end and cnd.isspace():
            result = self.last_sample_ok.lower() == 'false'
        else:
            # cnd may be null if next() called us
            result = eval(cnd)

        log.debug(f'while condition result:[ {result} ]')
        return result

    def next_is_null(self):
        """@override"""
        self.re_initialize()
        if self.end_of_loop(True):
            self.reset_break_loop()
            self.reset_loop_count()
            return None

        return self.next()

    def trigger_end_of_loop(self):
        """@override"""
        super().trigger_end_of_loop()
        self.end_of_loop(True)
        self.reset_loop_count()

    def next(self):
        """@override"""
        self.update_iteration_index(self.name, self.iter_count)
        try:
            if self.first and self.end_of_loop(False):
                self.reset_break_loop()
                self.reset_loop_count()
                return None
            return super().next()
        except Exception:
            ...
        finally:
            self.update_iteration_index(self.name, self.iter_count)

    def reset_loop_count(self):
        self.reset_iter_count()

    def startNextLoop(self):
        """@override"""
        self.re_initialize()

    def reset_break_loop(self):
        if self._break_loop:
            self._break_loop = False

    def break_loop(self):
        """@override"""
        self._break_loop = True
        self.first = True
        self.reset_current()
        self.reset_loop_count()

    def iteration_start(self, source, iter_count):
        """@override"""
        self.re_initialize()
        self.reset_loop_count()
