#!/usr/bin python3
# @File    : signature_util.py
# @Time    : 2023-06-14 15:51:55
# @Author  : Kelvin.Ye


def sort_fields(data: dict):
    """根据首字母排序"""
    return dict(sorted(data.items(), key=lambda x: x[0])) if data else {}
