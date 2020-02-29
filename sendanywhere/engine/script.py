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
        'ConfigTestElement': 'sendanywhere.testelement.test_element',
        'HTTPHeaders': 'sendanywhere.configs.http_headers',
        'LoopController': 'sendanywhere.controls.loop_controller',
        'IfController': 'sendanywhere.controls.if_controller',
        'CoroutineCollection': 'sendanywhere.coroutines.collection',
        'CoroutineGroup': 'sendanywhere.coroutines.group',
        'PythonPreProcessor': 'sendanywhere.processors.python_pre',
        'PythonPostProcessor': 'sendanywhere.processors.python_post',
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
        script: [dict] = json_util.from_json(content)
        nodes = cls.__parse(script)
        if not nodes:
            raise ScriptParseException('脚本为空或脚本已被禁用')
        root_tree = HashTree()
        for node, hash_tree in nodes:
            root_tree.put(node, hash_tree)
        return root_tree

    @classmethod
    def __parse(cls, script: [dict]) -> [(object, HashTree)]:
        # 校验节点是否有必须的属性
        cls.__check(script)
        nodes = []
        for item in script:
            # 过滤 enabled=False的节点(已禁用的节点)
            if not item.get('enabled'):
                continue

            node = cls.__get_node(item)
            child = item.get('child')

            if child:  # 存在子节点时递归解析
                child_nodes = cls.__parse(child)
                if child_nodes:
                    hash_tree = HashTree()
                    for child_node, child_hash_tree in child_nodes:
                        hash_tree.put(child_node, child_hash_tree)
                    nodes.append((node, hash_tree))
            else:
                nodes.append((node, HashTree()))
        return nodes

    @classmethod
    def __check(cls, script: [dict]) -> None:
        if not script:
            raise ScriptParseException('脚本解析失败，当前节点为空')
        for itme in script:
            if 'name' not in itme:
                raise ScriptParseException('脚本解析失败，当前节点缺少 name属性')
            if 'comments' not in itme:
                raise ScriptParseException('脚本解析失败，当前节点缺少 comments属性')
            if 'class' not in itme:
                raise ScriptParseException('脚本解析失败，当前节点缺少 class属性')
            if 'enabled' not in itme:
                raise ScriptParseException('脚本解析失败，当前节点缺少 enabled属性')
            if 'property' not in itme:
                raise ScriptParseException('脚本解析失败，当前节点缺少 property属性')
            if 'child' not in itme:
                raise ScriptParseException('脚本解析失败，当前节点缺少 child属性')

    @classmethod
    def __get_node(cls, script: dict) -> TestElement:
        """根据脚本中节点的 class属性转换为对应的 class对象

        Args:
            script: 脚本节点

        Returns:    object

        """
        # 获取 TestElement类
        class_name = script.get('class')
        clazz = cls.__get_class(class_name)

        # 实例化 TestElement实现类
        node = clazz(script.get('name'), script.get('comments'), script.get('property'))

        return node

    @classmethod
    def __get_class(cls, name: str) -> type:
        """根据类名获取类

        Args:
            name:   类名

        Returns:    类

        """
        module_path = cls.module_path.get(name)
        if not module_path:
            raise ScriptParseException(f'class_name={name} 找不到对应的节点类名称')

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
