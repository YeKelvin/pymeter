#!/usr/bin python3
# @File    : random_choice.py
# @Time    : 2021-08-18 09:13:37
# @Author  : Kelvin.Ye
import random
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class RandomChoice(Function):

    REF_KEY: Final = '__RandomChoice'

    def __init__(self):
        self.seq = None

    def execute(self):
        logger.debug(f'开始执行函数:[ {self.REF_KEY} ]')

        seq = self.seq.execute().strip().split(',')
        seq = [s.strip() for s in seq]

        result = str(random.choice(seq))
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 1)
        # 提取参数
        self.seq = params[0]
