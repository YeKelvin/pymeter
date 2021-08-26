#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : if_controller.py
# @Time    : 2020/2/29 10:49
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.controls.generic_controller import GenericController
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class IfController(GenericController):

    CONDITION: Final = 'IfController__condition'
