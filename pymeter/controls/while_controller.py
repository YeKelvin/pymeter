#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : while_controller.py
# @Time    : 2021-08-26 18:08:15
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.controls.generic_controller import GenericController
from pymeter.groups.context import ContextService
from pymeter.groups.context import CoroutineContext
from pymeter.groups.group import Coroutine
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class WhileController(GenericController):

    CONDITION: Final = 'WhileController__condition'

    @property
    def condition(self) -> str:
        return self.get_property_as_str(self.CONDITION)

    @property
    def ctx(self) -> CoroutineContext:
        return ContextService.get_context()

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
        res = False

        # If blank, only check previous sample when at end of loop
        if (self.break_loop and cnd.isspace()) or (cnd.lower() == 'last'):
            res = self.last_sample_ok.lower() == 'false'
        else:
            # cnd may be null if next() called us
            res = cnd.lower() == 'false'

        log.debug(f'Condition value:[ {res} ]')
        return res
