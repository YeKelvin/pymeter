#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_pre.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
import traceback
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.engine.globalization import GlobalUtils
from pymeter.processors.pre import PreProcessor
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonPreProcessor(PreProcessor, TestElement):

    # 脚本内容
    SCRIPT: Final = 'PythonPreProcessor__script'

    @property
    def script(self) -> str:
        return self.get_property_as_str(self.SCRIPT)

    def process(self) -> None:
        try:
            local_vars = {
                'log': log,
                'ctx': self.context,
                'vars': self.context.variables,
                'props': GlobalUtils.get_properties(),
                'prev': self.context.previous_result,
                'sampler': self.context.current_sampler
            }
            exec(self.script, {}, local_vars)
        except Exception:
            log.error(traceback.format_exc())
