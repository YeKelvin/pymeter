#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : traverser_test
# @Time    : 2020/2/26 10:49
# @Author  : Kelvin.Ye
import os

from sendanywhere.coroutines.collection import CoroutineCollection
from sendanywhere.engine.collection.traverser import SearchByClass
from sendanywhere.engine.script import ScriptServer
from sendanywhere.utils.path_util import __PROJECT_PATH__


class TestSearchByClass:
    def test_search_by_class(self):
        with open(os.path.join(__PROJECT_PATH__, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = ScriptServer.load_tree(script)
            searcher = SearchByClass(CoroutineCollection)
            tree.traverse(searcher)
            result = searcher.get_search_result()
            print(result)
