#!/usr/bin python3
# @File    : python_post.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.processors.post import PostProcessor
from pymeter.tools.python_code_snippets import DEFAULT_LOCAL_IMPORT_MODULE
from pymeter.tools.python_code_snippets import INDENT
from pymeter.workers.context import ContextService


class PythonPostProcessor(PostProcessor):

    # 脚本内容
    SCRIPT: Final = 'PythonPostProcessor__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    @property
    def raw_function(self):
        func = [
            'def function(log, ctx, args, vars, props, result, sampler):\n',
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
        try:
            ctx = ContextService.get_context()
            params = {'self': self}
            exec(self.raw_function, params, params)
            self.dynamic_function(  # noqa
                log=logger,
                ctx=ctx,
                args=ctx.arguments,
                vars=ctx.variables,
                props=ctx.properties,
                result=ctx.previous_result,
                sampler=ctx.current_sampler
            )
        except Exception:
            logger.exception('Exception Occurred')
