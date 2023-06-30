#!/usr/bin python3
# @File    : enums.py
# @Time    : 2023-05-22 14:45:31
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class ElementLevel(Enum):

    # 0空间
    WORKSPACE = 0

    # 1集合
    COLLECTION = 1

    # 2工作线程
    WORKER = 2

    # 3控制器
    CONTROLLER = 3

    # 4取样器
    SAMPLER = 4
