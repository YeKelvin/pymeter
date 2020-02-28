#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_test
# @Time    : 2020/2/25 15:17
# @Author  : Kelvin.Ye
import os

from sendanywhere.engine.script import ScriptServer
from sendanywhere.utils.path_util import __PROJECT_PATH__


class TestScriptServer:
    def test_load_tree(self):
        with open(os.path.join(__PROJECT_PATH__, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = ScriptServer.load_tree(script)
            print(tree)
            print(tree.index(0).list())
