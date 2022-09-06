#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_post.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.groups.context import ContextService
from pymeter.processors.post import PostProcessor
from pymeter.tools.python_code_snippets import DEFAULT_LOCAL_IMPORT_MODULE
from pymeter.tools.python_code_snippets import INDENT
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonPostProcessor(PostProcessor):

    # 脚本内容
    SCRIPT: Final = 'PythonPostProcessor__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    @property
    def raw_function(self):
        func = [
            'def function(log, ctx, vars, props, sampler, result):\n',
            DEFAULT_LOCAL_IMPORT_MODULE
        ]

        content = self.script
        if not content or content.isspace():  # 脚本内容为空则生成空函数
            func.append(f'{INDENT}...\n')
        else:
            lines = content.split('\n')
            func.extend(f'{INDENT}{line}\n' for line in lines)
        func.append('self.dynamic_function = function')
        return ''.join(func)

    def process(self) -> None:
        # noinspection PyBroadException
        try:
            ctx = ContextService.get_context()
            props = ctx.properties
            params = {'self': self}
            exec(self.raw_function, params, params)
            self.dynamic_function(  # noqa
                log=log,
                ctx=ctx,
                vars=ctx.variables,
                props=props,
                sampler=ctx.current_sampler,
                result=ctx.previous_result
            )
        except Exception:
            log.error(traceback.format_exc())
