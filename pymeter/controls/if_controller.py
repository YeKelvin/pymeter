#!/usr/bin python3
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
        self._done = val

    def next(self):
        """@override"""
        # We should only evaluate the condition if it is the first
        # time ( first "iteration" ) we are called.
        # For subsequent calls, we are inside the IfController,
        # so then we just pass the control to the next item inside the if control
        if not self.first:
            self.initialize_sub_controllers()
            return self.next_is_null()

        # 逻辑运算
        condition = self.condition.strip()
        result = self.evaluate(condition) if self.first else True
        logger.info(
            f'线程:[ {self.ctx.thread_name} ] 控制器:[ {self.name} ] IF逻辑运算\n'
            f'if条件: {condition}\n'
            f'if结果: {result}'
        )
        if result is True:
            return super().next()

        # if-result is false, need to re-initialize indexes
        try:
            self.initialize_sub_controllers()
            return self.next_is_null()
        except NextIsNullException:
            return None

    def trigger_end_of_loop(self):
        super().initialize_sub_controllers()
        super().trigger_end_of_loop()

    @staticmethod
    def evaluate(condition: str):
        # noinspection PyBroadException
        try:
            return eval(condition.replace('\r', '').replace('\n', '').replace('\t', ''))
        except Exception:
            logger.exception('Exception Occurred')
            return False
