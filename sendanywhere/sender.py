#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sender.py
# @Time    : 2020/2/12 11:46
# @Author  : Kelvin.Ye
import time

from sendanywhere.engine.globalization import SenderUtils
from sendanywhere.engine.script import ScriptServer
from sendanywhere.engine.standard_engine import StandardSenderEngine
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Sender:

    @staticmethod
    def start():
        now = time.time()
        ymd = time.strftime("%Y-%m-%d", time.localtime(now))
        hms = time.strftime("%H:%M:%S", time.localtime(now))

        SenderUtils.set_property('START.MS', int(now * 1000))
        SenderUtils.set_property('START.YMD', ymd)
        SenderUtils.set_property('START.HMS', hms)

        # 校验 script脚本不能为空

        Sender.run('')

    @staticmethod
    def run(script_content):
        # 加载脚本
        tree = ScriptServer.load_tree(script_content)

        # 删除禁用的节点

        engine = StandardSenderEngine()
        # 执行测试
        log.info('开始执行测试')
        engine.run_test()
