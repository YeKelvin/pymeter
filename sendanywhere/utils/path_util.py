#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : path_util
# @Time    : 2020/1/19 13:51
# @Author  : Kelvin.Ye
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
RESOURCES_PATH = os.path.join(PROJECT_PATH, 'resources')
SRC_PATH = os.path.join(PROJECT_PATH, 'sendanywhere')


def add_project_to_pth():
    sys.path.append(SRC_PATH)

