#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script.py
# @Time    : 2020/2/20 21:13
# @Author  : Kelvin.Ye
import importlib

from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.engine.exceptions import ScriptParseException
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import json_util
from sendanywhere.utils.log_util import get_logger

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
            content:    脚本内容

        Returns:        脚本的 HashTree对象

        """
        script: dict = json_util.from_json(content)
        node, hash_tree = cls.__parse(script)
        if (node is None) or (hash_tree is None):
            raise ScriptParseException('脚本为空或脚本已被禁用')
        root_tree = HashTree(node)
        root_tree.put(node, hash_tree)
        return root_tree

    @classmethod
    def __parse(cls, script: dict) -> (object, HashTree):
        cls.__check(script)
        if not script.get('enabled'):
            return None, None

        node = cls.__get_node(script)
        child = script.get('child')

        if child:
            child_node, child_hash_tree = cls.__parse(child)
            if (child_node is not None) and (child_hash_tree is not None):  # 过滤 enabled=False的节点(已禁用的节点)
                hash_tree = HashTree(child_node)
                hash_tree.put(child_node, child_hash_tree)
                return node, hash_tree

        return node, HashTree()

    @classmethod
    def __check(cls, script: dict) -> None:
        if not script:
            raise ScriptParseException('脚本解析失败，当前节点为空')
        if 'name' not in script:
            raise ScriptParseException('脚本解析失败，当前节点缺少 name属性')
        if 'comments' not in script:
            raise ScriptParseException('脚本解析失败，当前节点缺少 comments属性')
        if 'class' not in script:
            raise ScriptParseException('脚本解析失败，当前节点缺少 class属性')
        if 'enabled' not in script:
            raise ScriptParseException('脚本解析失败，当前节点缺少 enabled属性')
        if 'property' not in script:
            raise ScriptParseException('脚本解析失败，当前节点缺少 property属性')
        if 'child' not in script:
            raise ScriptParseException('脚本解析失败，当前节点缺少 child属性')

    @classmethod
    def __get_node(cls, script: dict) -> TestElement:
        # 获取 TestElement类对象
        class_name = script.get('class')
        clazz = cls.__get_class(class_name)

        # 实例化 TestElement实现类
        node = clazz(script.get('name'), script.get('comments'), script.get('property'))

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
