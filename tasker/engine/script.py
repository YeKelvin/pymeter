#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script.py
# @Time    : 2020/2/20 21:13
# @Author  : Kelvin.Ye
import importlib
import os
from typing import Iterable
from typing import List
from typing import Tuple

from tasker.common.exceptions import ScriptParseException
from tasker.elements.element import TaskElement
from tasker.engine.collection.tree import HashTree
from tasker.utils import json_util
from tasker.utils.log_util import get_logger


log = get_logger(__name__)

__MODULE_PATH__ = {
    # 测试集合
    'TaskCollection': 'tasker.elements.collection',

    # 任务组
    'TaskGroup': 'tasker.groups.group',

    # 断言器
    'JsonPathAssertion': 'tasker.assertions.json_path_assertion',
    'PythonAssertion': 'tasker.assertions.python_assertion',

    # 配置器
    'TestConfig': 'tasker.configs.test_config',
    'HttpHeader': 'tasker.configs.http_headers',
    'HttpHeaderManager': 'tasker.configs.http_headers',

    # 逻辑控制器
    'LoopController': 'tasker.controls.loop_controller',
    'IfController': 'tasker.controls.if_controller',

    # 前置处理器
    'PythonPreProcessor': 'tasker.processors.python_pre_processor',

    # 后置处理器
    'PythonPostProcessor': 'tasker.processors.python_post_processor',

    # Sampler
    'TestSampler': 'tasker.samplers.test_sampler',
    'HTTPSampler': 'tasker.samplers.http_sampler',
    'PythonSampler': 'tasker.samplers.python_sampler',
    'SQLSampler': 'tasker.samplers.sql_sampler',

    # 监听器
    'ResultCollector': 'tasker.listeners.result_collector',
    'SocketResultCollector': 'tasker.listeners.socket_result_collector',
    'FlaskSocketIOResultCollector': 'tasker.listeners.flask_socketio_result_collector'
}


class ScriptServer:

    @classmethod
    def load_tree(cls, source: str) -> HashTree:
        """读取脚本并返回脚本的HashTree对象"""
        script = cls.__loads_script(source)
        nodes = cls.__parse(script)
        if not nodes:
            raise ScriptParseException('脚本为空或脚本已被禁用')

        root_tree = HashTree()
        for node, hash_tree in nodes:
            root_tree.put(node, hash_tree)
        return root_tree

    @classmethod
    def __loads_script(cls, source) -> List[dict]:
        """反序列化脚本"""
        script = []
        if isinstance(source, list):
            script = source
        elif isinstance(source, str):
            try:
                script = json_util.from_json(source)
            except Exception:
                if os.path.exists(source):
                    with open(source, 'r', encoding='utf-8') as f:
                        json = ''.join(f.readlines())
                        script = json_util.from_json(json)
                else:
                    raise
        return script

    @classmethod
    def __parse(cls, script: Iterable[dict]) -> List[Tuple[object, HashTree]]:
        # 校验节点是否有必须的属性
        cls.__check(script)
        nodes = []
        for item in script:
            # 过滤enabled=False的节点(已禁用的节点)
            if not item.get('enabled'):
                continue

            node = cls.__get_node(item)
            children = item.get('children')

            if children:  # 存在子节点时递归解析
                children_node = cls.__parse(children)
                if children_node:
                    hash_tree = HashTree()

                    for child_node, child_hash_tree in children_node:
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
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 name 属性，item:[ {item} ]')
            if 'remark' not in item:
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 remark 属性，item:[ {item} ]')
            if 'class' not in item:
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 class 属性，item:[ {item} ]')
            if 'enabled' not in item:
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 enabled 属性，item:[ {item} ]')
            if 'property' not in item:
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 property 属性，item:[ {item} ]')
            if 'children' not in item:
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 children 属性，item:[ {item} ]')

    @classmethod
    def __get_node(cls, script: dict) -> TaskElement:
        """根据元素的class属性实例化为对象"""
        # 获取节点的类型
        class_name = script.get('class')

        # 根据类型名称获取type对象
        class_type = cls.__get_class_type(class_name)

        # 实例化节点
        node = class_type()
        node.set_property_by_replace(TaskElement.LABEL, script.get('name'))
        node.set_property_by_replace(TaskElement.REMARK, script.get('remark'))

        # 设置节点的属性
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
                cls.__set_object_property(node, key, value)
            elif isinstance(value, list):
                cls.__set_collection_property(node, key, value)

    @classmethod
    def __set_object_property(cls, node, key, value):
        if 'class' in value:
            propnode = cls.__get_node(value)
            node.set_property(key, propnode)
        else:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 class 属性，key:[ {key} ]')

    @classmethod
    def __set_collection_property(cls, node, key, value):
        collection = []
        for item in value:
            if isinstance(item, dict):
                if 'class' in item:
                    propnode = cls.__get_node(item)
                    collection.append(propnode)
                else:
                    raise ScriptParseException(f'脚本解析失败，当前节点缺少 class 属性，key:[ {key} ]')
            else:
                raise ScriptParseException(f'脚本解析失败，当前节点缺少 class 属性，key:[ {key} ]')
        node.set_property(key, collection)

    @classmethod
    def __get_class_type(cls, name: str) -> type:
        """根据类名获取类

        Args:
            name: 类名

        Returns:
            type

        """
        module_path = __MODULE_PATH__.get(name)
        if not module_path:
            raise ScriptParseException(f'找不到对应节点的类型名称:[ {name} ] ')

        module = importlib.import_module(module_path)
        return getattr(module, name)

    @classmethod
    def save_tree(cls, tree):
        """序列化脚本对象"""
        ...
