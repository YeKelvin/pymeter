#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : if_controller.py
# @Time    : 2020/2/29 10:49
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.controls.generic_controller import GenericController
from pymeter.tools.exceptions import NextIsNullException


class IfController(GenericController):

    CONDITION: Final = 'IfController__condition'

    @property
    def condition(self) -> str:
        return self.get_property_as_str(self.CONDITION)

    @property
    def done(self):
        return False

    @done.setter
    def done(self, val: bool):
        logger.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] set done:[ {val} ]')
        self._done = val

    def next(self):
        """@override"""
        # We should only evaluate the condition if it is the first
        # time ( first "iteration" ) we are called.
        # For subsequent calls, we are inside the IfControllerGroup,
        # so then we just pass the control to the next item inside the if control
        cnd = self.condition.strip()
        logger.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] if condition:[ {cnd} ]')
        result = self.evaluate(cnd) if self.first else True
        logger.debug(
            f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] if condition result:[ {result} ]')
        if result is True:
            return super().next()

        # If-test is false, need to re-initialize indexes
        try:
            self.initialize_sub_controllers()
            return self.next_is_null()
        except NextIsNullException:
            return None

    def trigger_end_of_loop(self):
        super().initialize_sub_controllers()
        super().trigger_end_of_loop()

    @staticmethod
    def evaluate(cnd: str):
        # noinspection PyBroadException
        try:
            return eval(cnd.replace('\r', '').replace('\n', '').replace('\t', ''))
        except Exception:
            logger.exception()
            return False
