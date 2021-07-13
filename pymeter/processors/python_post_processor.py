#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_post.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.engine.globalization import GlobalUtils
from pymeter.groups.context import ContextService
from pymeter.processors.post import PostProcessor
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonPostProcessor(PostProcessor):

    # 脚本内容
    SCRIPT: Final = 'PythonPostProcessor__script'

    def process(self) -> None:
        try:
            ctx = ContextService.get_context()
            props = GlobalUtils.get_properties()
            local_vars = {
                'log': log,
                'ctx': ctx,
                'vars': ctx.variables,
                'props': props,
                'prev': ctx.previous_result
            }
            exec(self.script, {}, local_vars)
        except Exception:
            log.error(traceback.format_exc())
