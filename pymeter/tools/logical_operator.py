#!/usr/bin python3
# @File    : logical_operator.py
# @Time    : 2023-05-29 16:41:18
# @Author  : Kelvin.Ye
from loguru import logger


def logical_calculate(rules: list, logic: str, actual_values: dict) -> bool:
    if not rules:
        return True

    if logic == 'AND':
        logger.debug(f'逻辑与运算，规则: {rules}')
        return all(calculate_condition(rule, actual_values) for rule in rules)
    elif logic == 'OR':
        logger.debug(f'逻辑或运算，规则: {rules}')
        return any(calculate_condition(rule, actual_values) for rule in rules)
    else:
        raise KeyError(f'运算符:[ {logic} ] 不支持的逻辑运算符')


def calculate_condition(rule: dict, actual_values: dict) -> bool:
    if 'logic' in rule:
        return logical_calculate(rule['rules'], rule['logic'], actual_values)

    field = rule['field']
    exists = field in actual_values
    if not exists:
        logger.debug(f'域:[ {field} ] 未提供域数据')
        return False

    operator = rule['operator']
    value = rule['value']

    result = None
    if operator == 'EQUAL':
        result = actual_values[field] == value
    elif operator == 'NOT_EQUAL':
        result = actual_values[field] != value
    elif operator == 'IN':
        result = actual_values[field] in value
    elif operator == 'NOT_IN':
        result = actual_values[field] not in value
    else:
        raise KeyError(f'运算符:[ {operator} ] 不支持的逻辑运算符')

    logger.debug(f'逻辑运算，规则: {rule}，实际值: {actual_values}, 结果: {result}')
    return result
