#!/usr/bin python3
# @File    : script.py
# @Time    : 2020/2/20 21:13
# @Author  : Kelvin.Ye
import importlib
from collections.abc import Iterable

from pymeter.elements.element import TestElement
from pymeter.elements.property import CollectionProperty
from pymeter.elements.property import DictProperty
from pymeter.engines.hashtree import HashTree
from pymeter.engines.replacer import ValueReplacer
from pymeter.engines.save_service import modules
from pymeter.tools.exceptions import ScriptParseError
from pymeter.utils.json_util import from_json


def load_tree(source) -> HashTree:
    """加载脚本"""
    script = __loads_script__(source)
    nodes = __parse_node__(script)

    if not nodes:
        raise ScriptParseError('脚本为空或脚本已禁用')

    root = HashTree()
    for node, hash_tree in nodes:
        root.put(node, hash_tree)
    return root


def __loads_script__(source) -> list[dict]:
    """反序列化脚本"""
    if isinstance(source, list):
        return source

    if not isinstance(source, str):
        raise ScriptParseError('不支持的脚本类型')

    script = from_json(source)
    if not isinstance(script, list):
        raise ScriptParseError('不支持的脚本类型')

    return script


def __parse_node__(script: Iterable[dict]) -> list[tuple[object, HashTree]]:
    if not script:
        raise ScriptParseError('脚本解析失败，当前节点为空')

    nodes = []
    for item in script:
        # 校验节点是否有必须的属性
        __check_attributes__(item)
        # 过滤已禁用的节点
        if not item.get('enabled'):
            continue
        # 实例化节点
        node = __init_node__(item)
        # 存在子节点时递归解析
        if children := item.get('children', None):
            if child_nodes := __parse_node__(children):
                hash_tree = HashTree()
                for child_node, child_hash_tree in child_nodes:
                    hash_tree.put(child_node, child_hash_tree)
                nodes.append((node, hash_tree))
        else:
            nodes.append((node, HashTree()))
    return nodes


def __check_attributes__(item: dict) -> None:
    if 'name' not in item:
        item.pop('children')  # 无需打印children内容
        raise ScriptParseError(f'节点:[ {item} ] 解析失败，节点缺少 name 属性，')
    if 'class' not in item:
        raise ScriptParseError(f'节点:[ {item["name"]} ] 解析失败，节点缺少 class 属性')
    if 'enabled' not in item:
        raise ScriptParseError(f'节点:[ {item["name"]} ] 解析失败，节点缺少 enabled 属性')
    if 'property' not in item:
        raise ScriptParseError(f'节点:[ {item["name"]} ] 解析失败，节点缺少 property 属性')


def __set_replaced_property__(element: TestElement, key: str, value: any) -> None:
    if key and value:
        element.add_property(key, ValueReplacer.replace_values(key, value))


def __init_node__(item: dict) -> TestElement:
    """根据元素的class属性实例化为对象"""
    # 节点类名
    class_name = item.get('class')
    # 节点类型
    class_type = __get_class_type__(class_name)
    # 实例化节点
    node = class_type()
    # 设置节点的属性
    __set_replaced_property__(node, TestElement.NAME, item.get('name'))
    __set_replaced_property__(node, TestElement.DESC, item.get('desc'))
    __set_properties__(node, item.get('property'))
    # 设置节点层级
    if (level := item.get('level')) is not None:
        node.level = level
    return node


def __set_properties__(node, props):
    if not props:
        return

    for key, value in props.items():
        if isinstance(value, str):
            __set_replaced_property__(node, key, value)
        elif isinstance(value, dict):
            __set_dict_property__(node, key, value)
        elif isinstance(value, list):
            __set_collection_property__(node, key, value)


def __set_dict_property__(node, key, value: dict):
    if 'class' in value:
        element = __init_node__(value)
        node.set_property(key, element)
    elif elements := {
        _key_: __init_node__(_value_)
        for _key_, _value_ in value.items()
        if 'class' in value
    }:
        node.add_property(key, DictProperty(key, elements))
    else:
        node.set_property(key, value)


def __set_collection_property__(node, key, value: list):
    if elements := [
        __init_node__(item)
        for item in value
        if isinstance(item, dict) and 'class' in item
    ]:
        node.add_property(key, CollectionProperty(key, elements))
    else:
        node.set_property(key, value)


def __get_class_type__(classname: str) -> type:
    """根据类名获取类"""
    module_path = modules.get(classname)
    if not module_path:
        raise ScriptParseError(f'类名:[ {classname} ] 节点类型不存在')

    module = importlib.import_module(module_path)
    return getattr(module, classname)
