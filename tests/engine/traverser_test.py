#!/usr/bin python3
# @File    : traverser_test.py
# @Time    : 2020/2/26 10:49
# @Author  : Kelvin.Ye
import pathlib

from pymeter.collections.test_collection import TestCollection
from pymeter.engine import script_service
from pymeter.engine.traverser import SearchByClass


class SearchByClassTest:

    def test_search_by_class(self):
        # 项目根目录
        rootpath = pathlib.Path(__file__).parent.parent.absolute()
        with open(rootpath.joinpath('scripts', 'debug.json')) as f:
            script = ''.join(f.readlines())
            tree = script_service.load_tree(script)
            searcher = SearchByClass(TestCollection)
            tree.traverse(searcher)
            result = searcher.get_search_result()
            print(result)
