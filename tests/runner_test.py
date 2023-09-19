#!/usr/bin python3
# @File    : sender_test
# @Time    : 2020/2/26 13:42
# @Author  : Kelvin.Ye
import os

from pymeter import config as CONFIG
from pymeter.runner import Runner


class TestRunner:
    def test_start(self):
        with open(os.path.join(CONFIG.PROJECT_PATH, 'docs', 'test-script.json'), encoding='utf-8') as f:
            script = ''.join(f.readlines())
            Runner.start(script)
