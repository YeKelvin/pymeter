#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_test
# @Time    : 2020/2/25 15:17
# @Author  : Kelvin.Ye
import os

from pymeter.engine.script_server import ScriptServer
from pymeter.engine.traverser import TreeCloner
from pymeter.utils.path_util import PROJECT_PATH


class ScriptServerTest:

    def test_load_tree(self):
        with open(os.path.join(PROJECT_PATH, 'docs', 'test-sampler.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = ScriptServer.load_tree(script)
            print(f'tree=\n{tree}')
            cloner = TreeCloner(True)
            tree.traverse(cloner)
            print(f'cloned_tree=\n{cloner.get_cloned_tree()}')


if __name__ == '__main__':
    with open(os.path.join(PROJECT_PATH, 'docs', 'script-v2.json'), 'r', encoding='utf-8') as f:
        script = ''.join(f.readlines())
        tree = ScriptServer.load_tree(script)
        print(f'tree=\n{tree}')
        collection = tree.list()[0]
        print(f'collection={collection}')
        group = tree.get_subtree(collection).list()[0]
        print(f'group={group}')
        print(f'main_controller={group.main_controller}')
        print(f'main_controller={group.main_controller.__dict__}')
