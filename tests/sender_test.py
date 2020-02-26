#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sender_test
# @Time    : 2020/2/26 13:42
# @Author  : Kelvin.Ye
import os

from sendanywhere.sender import Sender
from sendanywhere.utils.path_util import __PROJECT_PATH__


class TestSender:
    def test_start(self):
        with open(os.path.join(__PROJECT_PATH__, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            Sender.start(script)
