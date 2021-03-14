#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script.py
# @Time    : 2020/2/20 21:13
# @Author  : Kelvin.Ye
import importlib
import os
from typing import List, Tuple, Iterable

from sendanywhere.engine.collection.tree import HashTree
from sendanywhere.engine.exceptions import ScriptParseException
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils import json_util
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class ScriptServer:
    module_path = {
        # 测试集合
        'TestCollection': 'sendanywhere.testelement.collection',

        # 协程组
        'CoroutineGroup': 'sendanywhere.coroutines.group',

        # 断言器
        'JsonPathAssertion': 'sendanywhere.assertions.json_path_assertion',
        'PythonAssertion': 'sendanywhere.assertions.python_assertion',

        # 配置器
        'TestConfig': 'sendanywhere.configs.test_config',
        'HttpHeader': 'sendanywhere.configs.http_headers',
        'HttpHeaderManager': 'sendanywhere.configs.http_headers',

        # 逻辑控制器
        'LoopController': 'sendanywhere.controls.loop_controller',
        'IfController': 'sendanywhere.controls.if_controller',

        # 前置处理器
        'PythonPreProcessor': 'sendanywhere.processors.python_pre_processor',

        # 后置处理器
        'PythonPostProcessor': 'sendanywhere.processors.python_post_processor',

        # 取样器
        'TestSampler': 'sendanywhere.samplers.test_sampler',
        'HTTPSampler': 'sendanywhere.samplers.http_sampler',
        'PythonSampler': 'sendanywhere.samplers.python_sampler',
        'SQLSampler': 'sendanywhere.samplers.sql_sampler',

        # 监听器
        'ResultCollector': 'sendanywhere.listeners.result_collector',
        'SocketResultCollector': 'sendanywhere.listeners.socket_result_collector',
        'FlaskSocketIOResultCollector': 'sendanywhere.listeners.flask_socketio_result_collector'
    }

    @classmethod
    def __deserial_script(cls, content) -> List[dict]:
        """反序列化脚本
        """
        script = []
        if isinstance(content, list):
            script = content
        elif isinstance(content, str):
            path_exists = os.path.exists(content)
            if not path_exists:
                script = json_util.from_json(content)
            else:
                with open(content, 'r', encoding='utf-8') as f:
                    json = ''.join(f.readlines())
                    script = json_util.from_json(json)
        return script

    @classmethod
    def load_tree(cls, content: str) -> HashTree:
        """脚本反序列化为对象

        Args:
            content:    脚本内容

        Returns:        脚本的 HashTree对象

        """
        script = cls.__deserial_script(content)
        nodes = cls.__parse(script)
        if not nodes:
            raise ScriptParseException('脚本为空或脚本已被禁用')
        root_tree = HashTree()
        for node, hash_tree in nodes:
            root_tree.put(node, hash_tree)
        return root_tree

    @classmethod
    def __parse(cls, script: Iterable[dict]) -> List[Tuple[object, HashTree]]:
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
    def __check(cls, script: Iterable[dict]) -> None:
        if not script:
            raise ScriptParseException('脚本解析失败，当前节点为空')
        for item in script:
            if 'name' not in item:
                raise ScriptParseException('脚本解析失败，当前节点缺少 name属性')
            if 'comments' not in item:
                raise ScriptParseException('脚本解析失败，当前节点缺少 comments属性')
            if 'class' not in item:
                raise ScriptParseException('脚本解析失败，当前节点缺少 class属性')
            if 'enabled' not in item:
                raise ScriptParseException('脚本解析失败，当前节点缺少 enabled属性')
            if 'property' not in item:
                raise ScriptParseException('脚本解析失败，当前节点缺少 property属性')
            if 'child' not in item:
                raise ScriptParseException('脚本解析失败，当前节点缺少 child属性')

    @classmethod
    def __get_node(cls, script: dict) -> TestElement:
        """根据元素的class属性实例化为对象

        Args:
            script: 脚本节点

        Returns:    object

        """
        # 获取 TestElement的类型
        class_name = script.get('class')
        # 根据 ClassName获取 Class对象
        clazz = cls.__get_class(class_name)

        # 实例化 TestElement
        node = clazz()
        node.set_property_by_replace(TestElement.LABEL, script.get('name'))
        node.set_property_by_replace(TestElement.COMMENTS, script.get('comments'))

        # 设置 TestElement的属性
        cls.__set_node_property(node, script.get('property'))

        return node

    @classmethod
    def __set_node_property(cls, node, property):
        if not property:
            return
        for key, value in property.items():
            if isinstance(value, str):
                node.set_property_by_replace(key, value)
            elif isinstance(value, dict):
                if 'class' in value:
                    sub_node = cls.__get_node(value)
                    node.set_property(key, sub_node)
                else:
                    raise ScriptParseException('脚本解析失败，当前节点缺少 class属性')
            elif isinstance(value, list):
                collection = []
                for item in value:
                    if isinstance(item, dict):
                        if 'class' in item:
                            sub_node = cls.__get_node(item)
                            collection.append(sub_node)
                        else:
                            raise ScriptParseException('脚本解析失败，当前节点缺少 class属性')
                    else:
                        raise ScriptParseException('脚本解析失败，当前节点缺少 class属性')
                node.set_property(key, collection)

    @classmethod
    def __get_class(cls, name: str) -> type:
        """根据类名获取类

        Args:
            name:   类名

        Returns:    类

        """
        module_path = cls.module_path.get(name)
        if not module_path:
            raise ScriptParseException(f'类名:[ {name} ] 找不到对应的节点类名称')

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
