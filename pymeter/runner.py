#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : runner.py
# @Time    : 2020/2/12 11:46
# @Author  : Kelvin.Ye
import time
import traceback

from pymeter.engine.script_server import ScriptServer
from pymeter.engine.standard_engine import StandardEngine
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Runner:

    @staticmethod
    def start(script: str) -> None:
        """脚本执行主入口"""
        now = time.time()
        ymd = time.strftime('%Y-%m-%d', time.localtime(now))
        hms = time.strftime('%H:%M:%S', time.localtime(now))

        log.info(f'START.MS={int(now * 1000)}')
        log.info(f'START.YMD={ymd}')
        log.info(f'START.HMS={hms}')

        # 校验 script脚本不能为空
        if not script:
            raise Exception('脚本不允许为空')

        log.debug(f'script json:\n{script}')
        try:
            Runner.run(script)
        except Exception:
            log.error(traceback.format_exc())

    @staticmethod
    def run(script: str) -> None:
        """加载并解析脚本，将脚本反序列化为 HashTree对象"""
        log.info('开始加载脚本')
        # 加载脚本
        hashtree = ScriptServer.load_tree(script)
        log.debug(f'script hashtree:\n{hashtree}')

        # 将脚本配置到执行引擎中
        engine = StandardEngine()
        engine.configure(hashtree)

        # 开始执行测试
        log.info('开始执行测试')
        engine.run_test()


if __name__ == '__main__':
    import os

    from pymeter.utils.path_util import PROJECT_PATH

    with open(os.path.join(PROJECT_PATH, 'docs', 'test-funciton.json'), 'r', encoding='utf-8') as f:
        script = ''.join(f.readlines())
        Runner.start(script)
