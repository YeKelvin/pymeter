#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : path_util
# @Time    : 2020/1/19 13:51
# @Author  : Kelvin.Ye
import os
import sys

__PROJECT_PATH__ = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
__RESOURCES_PATH__ = os.path.join(__PROJECT_PATH__, 'resources')
__SRC_PATH__ = os.path.join(__PROJECT_PATH__, 'send-anywhere')


def add_project_to_pth():
    sys.path.append(__SRC_PATH__)

