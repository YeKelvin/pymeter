#!/usr/bin python3
# @File    : script_test
# @Time    : 2020/2/25 15:17
# @Author  : Kelvin.Ye
import os

from pymeter import config as CONFIG
from pymeter.engine import script_server
from pymeter.engine.traverser import TreeCloner


class ScriptServerTest:

    def test_load_tree(self):
        with open(os.path.join(CONFIG.PROJECT_PATH, 'docs', 'test-sampler.json'), encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = script_server.load_tree(script)
            print(f'tree=\n{tree}')
            cloner = TreeCloner(True)
            tree.traverse(cloner)
            print(f'cloned_tree=\n{cloner.get_cloned_tree()}')
