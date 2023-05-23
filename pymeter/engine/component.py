#!/usr/bin python3
# @File    : component.py
# @Time    : 2023-05-23 14:19:46
# @Author  : Kelvin.Ye


from copy import deepcopy


class Component:

    # 包含的组件类型
    INCLUDE_TYPE = 'Component__include_type'
    # 包含的组件层级
    INCLUDE_LEVEL = 'Component__include_level'

    # 排除的组件类型
    EXCLUDE_TYPE = 'Component__exclude_type'
    # 排除的组件层级
    EXCLUDE_LEVEL = 'Component__exclude_level'

    # 倒序执行
    ORDER_REVERSE = 'Component__order_reverse'

    # 倒序执行前置处理器
    REVERSE_PRE = 'Component__reverse_pre'

    # 倒序执行后置处理器
    REVERSE_POST = 'Component__reverse_post'

    # 倒序执行断言器
    REVERSE_ASSERT = 'Component__reverse_assert'

    @staticmethod
    def initial_config(collection_config, worker_config) -> dict:
        include = collection_config.get('include', {})
        exclude = collection_config.get('exclude', {})
        config = {
            Component.INCLUDE_TYPE: include.get('type', []),
            Component.INCLUDE_LEVEL: include.get('level', []),
            Component.EXCLUDE_TYPE: exclude.get('type', []),
            Component.EXCLUDE_LEVEL: exclude.get('level', []),
            Component.ORDER_REVERSE: collection_config.get('reverse', []),
        }

        include = worker_config.get('include', {})
        exclude = worker_config.get('exclude', {})
        if include_type := include.get('type'):
            config[Component.INCLUDE_TYPE] = include_type
        if include_level := include.get('level'):
            config[Component.INCLUDE_LEVEL] = include_level
        if exclude_type := exclude.get('type'):
            config[Component.EXCLUDE_TYPE] = exclude_type
        if exclude_level := exclude.get('level'):
            config[Component.EXCLUDE_LEVEL] = exclude_level
        if order_reverse := worker_config.get('reverse'):
            config[Component.ORDER_REVERSE] = order_reverse

        return config

    @staticmethod
    def merged_config(config, source):
        if not config:
            return source

        include = config.get('include', {})
        exclude = config.get('exclude', {})
        merged_config = deepcopy(source)

        if include_type := include.get('type'):
            merged_config[Component.INCLUDE_TYPE] = include_type
        if include_level := include.get('level'):
            merged_config[Component.INCLUDE_LEVEL] = include_level
        if exclude_type := exclude.get('type'):
            merged_config[Component.EXCLUDE_TYPE] = exclude_type
        if exclude_level := exclude.get('level'):
            merged_config[Component.EXCLUDE_LEVEL] = exclude_level
        if order_reverse := config.get('reverse'):
            merged_config[Component.ORDER_REVERSE] = order_reverse

        order_reverse = merged_config[Component.ORDER_REVERSE]
        merged_config[Component.REVERSE_PRE] = 1 in order_reverse
        merged_config[Component.REVERSE_POST] = 2 in order_reverse
        merged_config[Component.REVERSE_ASSERT] = 3 in order_reverse

        return merged_config
