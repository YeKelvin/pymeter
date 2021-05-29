#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sender_test
# @Time    : 2020/2/26 13:42
# @Author  : Kelvin.Ye
import os

from taskmeter.runner import Runner
from taskmeter.utils.path_util import PROJECT_PATH


class TestRunner:
    def test_start(self):
        with open(os.path.join(PROJECT_PATH, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            Runner.start(script)
