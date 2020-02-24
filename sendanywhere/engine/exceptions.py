#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exception.py
# @Time    : 2019/3/15 10:48
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class InvalidVariableException(Exception):
    pass


class SenderEngineException(Exception):
    pass


class ScriptParseException(Exception):
    pass
