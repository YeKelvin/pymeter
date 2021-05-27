#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_pre.py
# @Time    : 2020/2/17 16:29
# @Author  : Kelvin.Ye
from typing import Final

from sendanywhere.processors.pre import PreProcessor
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger


log = get_logger(__name__)


class PythonPreProcessor(PreProcessor, TestElement):
    SOURCE: Final = 'PythonPreProcessor__source'

    def process(self) -> None:
        exec(self.get_property_as_str(self.SOURCE), {}, locals())
