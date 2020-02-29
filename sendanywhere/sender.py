#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sender.py
# @Time    : 2020/2/12 11:46
# @Author  : Kelvin.Ye
import time

from sendanywhere.engine.script import ScriptServer
from sendanywhere.engine.standard_engine import StandardEngine
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Sender:

    @staticmethod
    def start(script: str):
        now = time.time()
        ymd = time.strftime("%Y-%m-%d", time.localtime(now))
        hms = time.strftime("%H:%M:%S", time.localtime(now))

        log.info(f'START.MS={int(now * 1000)}')
        log.info(f'START.YMD={ymd}')
        log.info(f'START.HMS={hms}')

        # 校验 script脚本不能为空
        if script:
            Sender.run(script)
        else:
            raise Exception('脚本不允许为空')

    @staticmethod
    def run(script: str):
        # 加载脚本
        tree = ScriptServer.load_tree(script)

        # 将脚本配置到测试引擎里
        engine = StandardEngine()
        engine.configure(tree)
        # 执行测试
        log.info('开始执行测试')
        engine.run_test()


if __name__ == '__main__':
    import os
    from sendanywhere.utils.path_util import __PROJECT_PATH__
    with open(os.path.join(__PROJECT_PATH__, 'docs', 'test-script.json'), 'r', encoding='utf-8') as f:
        script = ''.join(f.readlines())
        Sender.start(script)
