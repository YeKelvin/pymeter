#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : google_auth.py
# @Time    : 2021-08-17 18:58:12
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.google_common import GoogleAuthenticate
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class GoogleAuth(Function):

    REF_KEY: Final = '__GoogleAuth'

    def __init__(self):
        self.secret_key = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        secret_key = self.secret_key.execute().strip()
        result = str(GoogleAuthenticate.get_code(secret_key))
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 1)

        self.secretkey = params[0]
