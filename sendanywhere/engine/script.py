#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script.py
# @Time    : 2020/2/20 21:13
# @Author  : Kelvin.Ye
from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.engine.exceptions import ScriptParseException
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import json_util
from sendanywhere.utils.log_util import get_logger
import importlib

log = get_logger(__name__)


class ScriptServer:
    module_path = {
        'JsonAssertion': 'sendanywhere.assertions.json_assertion',
        'PythonAssertion': 'sendanywhere.assertions.python_assertion',
        'HTTPHeaders': 'sendanywhere.configs.http_headers.py',
        'CoroutineCollection': 'sendanywhere.coroutines.collection',
        'CoroutineGroup': 'sendanywhere.coroutines.group',
        'PythonPreProcessor': 'sendanywhere.processor.python_pre',
        'PythonPostProcessor': 'sendanywhere.processor.python_post',
        'HTTPSampler': 'sendanywhere.samplers.http_sampler',
        'PythonSampler': 'sendanywhere.samplers.python_sampler',
        'SQLSampler': 'sendanywhere.samplers.sql_sampler',
    }

    @classmethod
    def load_tree(cls, content: str) -> HashTree:
        """脚本反序列化为对象

        Args:
            script:

        Returns:

        """
        script: dict = json_util.from_json(content)
        hast_tree = HashTree()
        cls.__parse(script)

    @classmethod
    def __parse(cls, script: dict):
        cls.__check(script)
        node = cls.__get_node(script)
        node_enabled = bool(script.get('enabled'))
        node_child = script.get('child')

    @classmethod
    def __check(cls, script: dict) -> None:
        if not script or not (
                hasattr(script, 'name') and
                hasattr(script, 'comments') and
                hasattr(script, 'class') and
                hasattr(script, 'enabled') and
                hasattr(script, 'property') and
                hasattr(script, 'child')
        ):
            raise ScriptParseException('脚本解析失败')

    @classmethod
    def __get_node(cls, script: dict) -> TestElement:
        # 获取 TestElement类对象
        class_name = script.get('class')
        clazz = cls.__get_class(class_name)

        # 实例化 TestElement实现类
        node = clazz(script.get('name'), script.get('comments'))

        # 设置 TestElement属性
        node_property = script.get('property')
        if node_property:
            for key, value in node_property.items():
                node.set_property(key, value)
        return node

    @classmethod
    def __get_class(cls, name: str) -> type:
        module_path = cls.module_path.get(name)
        if not module_path:
            raise ScriptParseException(f'className={name} 找不到对应的节点类名称')
        module = importlib.import_module(module_path)
        return getattr(module, name)

    @classmethod
    def save_tree(cls, tree):
        """序列化脚本对象

        Args:
            tree:

        Returns:

        """
        pass


if __name__ == '__main__':
    module = importlib.import_module('sendanywhere.testelement.test_element')
    TestElement = getattr(module, 'TestElement')
    testelement = TestElement()
    print(testelement.__dict__)
