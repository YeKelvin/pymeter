#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function
# @Time    : 2020/1/19 17:05
# @Author  : Kelvin.Ye
from sendanywhere.engine.exceptions import InvalidVariableException
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Function:
    REF_KEY = '__referenceKey'

    def execute(self):
        raise NotImplementedError

    def set_parameters(self, parameters: list):
        raise NotImplementedError

    def check_parameter_count(self, parameters: list, count: int) -> None:
        num = len(parameters)
        if num != count:
            raise InvalidVariableException(
                f'{self.REF_KEY} called with wrong number of parameters. Actual: {num}. Expected: {count}.'
            )

    def check_parameter_min(self, parameters: list, minimum: int) -> None:
        num = len(parameters)
        if num < minimum:
            raise InvalidVariableException(
                f'{self.REF_KEY} called with wrong number of parameters. Actual: {num}. Expected at least: {minimum}.'
            )

    def check_parameter_max(self, parameters: list, maximum: int = None) -> None:
        num = len(parameters)
        if num > maximum:
            raise InvalidVariableException(
                f'{self.REF_KEY} called with wrong number of parameters. Actual: {num}. Expected at most: {maximum}.'
            )
