#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_post.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.groups.context import ContextService
from pymeter.processors.post import PostProcessor
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonPostProcessor(PostProcessor):

    # 脚本内容
    SCRIPT: Final = 'PythonPostProcessor__script'

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
            # 定义脚本中可用的内置变量
            params = {
                'log': log,
                'ctx': ctx,
                'vars': ctx.variables,
                'props': props,
                'result': ctx.previous_result
            }
            exec(script, params, params)
        except Exception:
            log.error(traceback.format_exc())
