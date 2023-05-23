#!/usr/bin python3
# @File    : traverser_test
# @Time    : 2020/2/26 10:49
# @Author  : Kelvin.Ye
import os

from pymeter import config as CONFIG
from pymeter.collections.collection import TestCollection
from pymeter.engine import script_server
from pymeter.engine.traverser import SearchByClass


class SearchByClassTest:

    def test_search_by_class(self):
        with open(os.path.join(CONFIG.PROJECT_PATH, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
            script = ''.join(f.readlines())
            tree = script_server.load_tree(script)
            searcher = SearchByClass(TestCollection)
            tree.traverse(searcher)
            result = searcher.get_search_result()
            print(result)
