#!/usr/bin python3
# @File    : script.py
# @Time    : 2020/2/20 21:13
# @Author  : Kelvin.Ye
import importlib
from typing import Iterable
from typing import List
from typing import Tuple

from loguru import logger

from pymeter.elements.element import TestElement
from pymeter.engine.tree import HashTree
from pymeter.engine.values import ValueReplacer
from pymeter.tools.exceptions import ScriptParseError
from pymeter.utils import json_util


MODULES = {
    # 测试集合
    'TestCollection': 'pymeter.engine.collection',

    # 测试分组
    'SetupGroup': 'pymeter.groups.group',
    'TestGroup': 'pymeter.groups.group',
    'TearDownGroup': 'pymeter.groups.group',

    # 配置器
    'Argument': 'pymeter.configs.arguments',
    'Arguments': 'pymeter.configs.arguments',
    'DatabaseEngine': 'pymeter.configs.database',
    'HTTPHeader': 'pymeter.configs.httpconfigs',
    'HTTPHeaderManager': 'pymeter.configs.httpconfigs',
    'HTTPCookieManager': 'pymeter.configs.httpconfigs',
    'HTTPSessionManager': 'pymeter.configs.httpconfigs',
    'VariableDataset': 'pymeter.configs.dataset',
    'TransactionHTTPSessionManager': 'pymeter.configs.transactions',
    'TransactionParameter': 'pymeter.configs.transactions',

    # 逻辑控制器
    'IfController': 'pymeter.controls.if_controller',
    'ForInController': 'pymeter.controls.forin_controller',
    'LoopController': 'pymeter.controls.loop_controller',
    'RetryController': 'pymeter.controls.retry_controller',
    'TransactionController': 'pymeter.controls.transaction',
    'WhileController': 'pymeter.controls.while_controller',

    # 时间控制器
    'ConstantTimer': 'pymeter.timers.constant_timer',

    # 取样器
    'HTTPSampler': 'pymeter.samplers.http_sampler',
    'PythonSampler': 'pymeter.samplers.python_sampler',
    'SQLSampler': 'pymeter.samplers.sql_sampler',

    # 前置处理器
    'PythonPreProcessor': 'pymeter.processors.python_pre_processor',
    'SleepPreProcessor': 'pymeter.processors.sleep_pre_processor',

    # 后置处理器
    'PythonPostProcessor': 'pymeter.processors.python_post_processor',
    'JsonPathPostProcessor': 'pymeter.processors.json_path_post_processor',
    'SleepPostProcessor': 'pymeter.processors.sleep_post_processor',

    # 断言器
    'PythonAssertion': 'pymeter.assertions.python_assertion',
    'JsonPathAssertion': 'pymeter.assertions.json_path_assertion',

    # 监听器
    'FlaskDBIterationStorage': 'pymeter.listeners.flask_db_iteration_storage',
    'FlaskDBResultStorage': 'pymeter.listeners.flask_db_result_storage',
    'FlaskSIOResultCollector': 'pymeter.listeners.flask_sio_result_collector',
    'ResultCollector': 'pymeter.listeners.result_collector',
    'SocketResultCollector': 'pymeter.listeners.socket_result_collector'
}


def load_tree(source) -> HashTree:
    """加载脚本"""
    logger.info('开始加载脚本')

    script = __loads_script__(source)
    nodes = __parse_node__(script)

    if not nodes:
        raise ScriptParseError('脚本为空或脚本已禁用')

    root = HashTree()
    for node, hash_tree in nodes:
        root.put(node, hash_tree)
    return root


def __loads_script__(source) -> List[dict]:
    """反序列化脚本"""
    if isinstance(source, list):
        return source

    if not isinstance(source, str):
        raise ScriptParseError('不支持的脚本类型')

    script = json_util.from_json(source)
    if not isinstance(script, list):
        raise ScriptParseError('不支持的脚本类型')

    return script


def __parse_node__(script: Iterable[dict]) -> List[Tuple[object, HashTree]]:
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


def __init_node__(script: dict) -> TestElement:
    """根据元素的class属性实例化为对象"""
    # 获取节点的类型
    class_name = script.get('class')
    logger.debug(f'node class:[ {class_name} ]')

    # 根据类型名称获取type对象
    class_type = __get_class_type__(class_name)

    # 实例化节点
    node = class_type()
    __set_replaced_property__(node, TestElement.NAME, script.get('name'))
    __set_replaced_property__(node, TestElement.REMARK, script.get('remark'))

    # 设置节点的属性
    __set_properties__(node, script.get('property'))

    return node


def __set_properties__(node, props):
    if not props:
        return

    for key, value in props.items():
        if isinstance(value, str):
            __set_replaced_property__(node, key, value)
        elif isinstance(value, dict):
            __set_object_property__(node, key, value)
        elif isinstance(value, list):
            __set_collection_property__(node, key, value)


def __set_object_property__(node, key, value: dict):
    if 'class' in value:
        propnode = __init_node__(value)
        node.set_property(key, propnode)
    else:
        node.set_property(key, value)


def __set_collection_property__(node, key, value: list):
    collection = []
    for item in value:
        if isinstance(item, dict) and 'class' in item:
            propnode = __init_node__(item)
            collection.append(propnode)
        else:
            collection.append(item)
    node.set_property(key, collection)


def __get_class_type__(classname: str) -> type:
    """根据类名获取类"""
    module_path = MODULES.get(classname)
    if not module_path:
        raise ScriptParseError(f'类名:[ {classname} ] 节点类型不存在')

    module = importlib.import_module(module_path)
    return getattr(module, classname)
