#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : traverser_test
# @Time    : 2020/2/26 10:49
# @Author  : Kelvin.Ye
import os

from pymeter.engine.collection import TestCollection
from pymeter.engine.traverser import SearchByClass
from pymeter.engine.script_server import ScriptServer
from pymeter.utils.path_util import PROJECT_PATH


class SearchByClassTest:

    def test_search_by_class(self):
        with open(os.path.join(PROJECT_PATH, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = ScriptServer.load_tree(script)
            searcher = SearchByClass(TestCollection)
            tree.traverse(searcher)
            result = searcher.get_search_result()
            print(result)
