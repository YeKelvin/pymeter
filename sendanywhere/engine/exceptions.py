#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exception.py
# @Time    : 2019/3/15 10:48
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class InvalidVariableException(Exception):
    pass


class EngineException(Exception):
    pass


class ScriptParseException(Exception):
    pass


class NextIsNullException(Exception):
    pass


class StopTestException(Exception):
    pass


class StopTestNowException(Exception):
    pass


class StopCoroutineException(Exception):
    pass
