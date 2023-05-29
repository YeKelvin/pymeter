#!/usr/bin python3
# @File    : logical_operator.py
# @Time    : 2023-05-29 16:41:18
# @Author  : Kelvin.Ye
from loguru import logger


def logical_calculate(rules: list, logic: str, data: dict) -> bool:
    if not rules:
        return True

    if logic == 'AND':
        logger.debug(f'逻辑与运算，规则: {rules}')
        return all(calculate_condition(rule, data) for rule in rules)
    elif logic == 'OR':
        logger.debug(f'逻辑或运算，规则: {rules}')
        return any(calculate_condition(rule, data) for rule in rules)
    else:
        raise KeyError(f'运算符:[ {logic} ] 不支持的逻辑运算符')


def calculate_condition(rule: dict, data: dict) -> bool:
    if 'logic' in rule:
        return logical_calculate(rule['rules'], rule['logic'], data)

    keyword = rule['keyword']
    exists = keyword in data
    if not exists:
        logger.debug(f'关键字:[ {keyword} ] 未提供关键字数据')
        return False

    operator = rule['operator']
    value = rule['value']
    result = None
    if operator == 'EQUAL':
        result = data[keyword] == value
    elif operator == 'NOT_EQUAL':
        result = data[keyword] != value
    elif operator == 'IN':
        result = data[keyword] in value
    elif operator == 'NOT_IN':
        result = data[keyword] not in value
    else:
        raise KeyError(f'运算符:[ {operator} ] 不支持的逻辑运算符')

    logger.debug(f'逻辑运算，规则: {rule}，结果: {result}')
    return result
