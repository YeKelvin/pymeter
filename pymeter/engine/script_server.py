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

from pymeter.common.exceptions import ScriptParseException
from pymeter.elements.element import TestElement
from pymeter.engine.tree import HashTree
from pymeter.utils import json_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)

__MODULE_PATH__ = {
    # 测试集合
    'TestCollection': 'pymeter.engine.collection',

    # TestGroup
    'TestGroup': 'pymeter.groups.group',

    # 断言器
    'JsonPathAssertion': 'pymeter.assertions.json_path_assertion',
    'PythonAssertion': 'pymeter.assertions.python_assertion',

    # 配置器
    'TestConfig': 'pymeter.configs.test_config',
    'HttpHeader': 'pymeter.configs.http_headers',
    'HttpHeaderManager': 'pymeter.configs.http_headers',

    # 逻辑控制器
    'LoopController': 'pymeter.controls.loop_controller',
    'IfController': 'pymeter.controls.if_controller',

    # 前置处理器
    'PythonPreProcessor': 'pymeter.processors.python_pre_processor',

    # 后置处理器
    'PythonPostProcessor': 'pymeter.processors.python_post_processor',

    # Sampler
    'TestSampler': 'pymeter.samplers.test_sampler',
    'HTTPSampler': 'pymeter.samplers.http_sampler',
    'PythonSampler': 'pymeter.samplers.python_sampler',
    'SQLSampler': 'pymeter.samplers.sql_sampler',

    # 监听器
    'ResultCollector': 'pymeter.listeners.result_collector',
    'SocketResultCollector': 'pymeter.listeners.socket_result_collector',
    'FlaskSocketIOResultCollector': 'pymeter.listeners.flask_socketio_result_collector'
}


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


def save_tree(cls, tree):
    """序列化脚本对象"""
    ...


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


def __check(cls, script: Iterable[dict]) -> None:
    if not script:
        raise ScriptParseException('脚本解析失败，当前节点为空')

    for item in script:
        if 'name' not in item:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 name 属性，item:[ {item} ]')
        if 'remark' not in item:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 remark 属性，节点名称:[ {item["name"]} ]')
        if 'class' not in item:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 class 属性，节点名称:[ {item["name"]} ]')
        if 'enabled' not in item:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 enabled 属性，节点名称:[ {item["name"]} ]')
        if 'propertys' not in item:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 propertys 属性，节点名称:[ {item["name"]} ]')
        if 'children' not in item:
            raise ScriptParseException(f'脚本解析失败，当前节点缺少 children 属性，节点名称:[ {item["name"]} ]')


def __get_node(cls, script: dict) -> TestElement:
    """根据元素的class属性实例化为对象"""
    # 获取节点的类型
    class_name = script.get('class')

    # 根据类型名称获取type对象
    class_type = cls.__get_class_type(class_name)

    # 实例化节点
    node = class_type()
    node.set_property_by_replace(TestElement.LABEL, script.get('name'))
    node.set_property_by_replace(TestElement.REMARK, script.get('remark'))

    # 设置节点的属性
    cls.__set_propertys(node, script.get('propertys'))

    return node


def __set_propertys(cls, node, propertys):
    if not propertys:
        return

    for key, value in propertys.items():
        if isinstance(value, str):
            node.set_property_by_replace(key, value)
        elif isinstance(value, dict):
            cls.__set_object_property(node, key, value)
        elif isinstance(value, list):
            cls.__set_collection_property(node, key, value)


def __set_object_property(cls, node, key, value):
    if 'class' in value:
        propnode = cls.__get_node(value)
        node.set_property(key, propnode)
    else:
        node.set_property(key, value)


def __set_collection_property(cls, node, key, value):
    collection = []
    for item in value:
        if isinstance(item, dict):
            if 'class' in item:
                propnode = cls.__get_node(item)
                collection.append(propnode)
            else:
                collection.append(item)
        else:
            collection.append(item)
    node.set_property(key, collection)


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
