#!/usr/bin python3
# @File    : python_sampler.py
# @Time    : 2020/2/16 21:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from loguru import logger

from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.tools.python_code_snippets import DEFAULT_LOCAL_IMPORT_MODULE
from pymeter.tools.python_code_snippets import INDENT


class PythonSampler(Sampler):

    # 元素配置
    CONFIG: Final = 'PythonSampler__config'

    # 请求类型
    REQUEST_TYPE: Final = 'PYTHON'

    # 脚本内容
    SCRIPT: Final = 'PythonSampler__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    @property
    def raw_function(self):
        func = ['def function(log, ctx, vars, props, prev, result):\n' + DEFAULT_LOCAL_IMPORT_MODULE]

        content = self.script
        if not content or content.isspace():  # 脚本内容为空则生成空函数
            func.append(f'{INDENT}...\n')
        else:
            lines = content.split('\n')
            func.extend(f'{INDENT}{line}\n' for line in lines)
        func.append('self.dynamic_function = function')
        return ''.join(func)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.request_data = self.script
        result.sample_start()

        # noinspection PyBroadException
        try:
            # 定义脚本中可用的内置变量
            params = {'self': self}
            exec(self.raw_function, params, params)
            ctx = ContextService.get_context()
            props = ctx.properties
            if res := self.dynamic_function(  # noqa
                log=logger,
                ctx=ctx,
                vars=ctx.variables,
                props=props,
                prev=ctx.previous_result,
                result=result
            ):
                result.response_data = res if isinstance(res, str) else str(res)
        except Exception:
            result.success = False
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()

        return result
