#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_test
# @Time    : 2020/2/25 15:17
# @Author  : Kelvin.Ye
import os

from taskmeter.engine.collection.traverser import TreeCloner
from taskmeter.engine.script import ScriptServer
from taskmeter.utils.path_util import PROJECT_PATH


class TestScriptServer:
    def test_load_tree(self):
        with open(os.path.join(PROJECT_PATH, 'docs', 'test-sampler.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = ScriptServer.load_tree(script)
            print(f'tree=\n{tree}')
            cloner = TreeCloner(True)
            tree.traverse(cloner)
            print(f'cloned_tree=\n{cloner.get_cloned_tree()}')
