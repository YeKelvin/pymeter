#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_pre.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.groups.context import ContextService
from pymeter.processors.pre import PreProcessor
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonPreProcessor(PreProcessor):

    # 脚本内容
    SCRIPT: Final = 'PythonPreProcessor__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    def process(self) -> None:
        script = self.script
        if not script:
            return
        script = 'import random\n' + script

        try:
            ctx = ContextService.get_context()
            props = ctx.properties
            locals = {
                'log': log,
                'ctx': ctx,
                'vars': ctx.variables,
                'props': props,
                'prev': ctx.previous_result,
                'sampler': ctx.current_sampler
            }
            exec(script, {}, locals)
        except Exception:
            log.error(traceback.format_exc())
