#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : runner.py
# @Time    : 2020/2/12 11:46
# @Author  : Kelvin.Ye
import time

from sendanywhere.engine.script import ScriptServer
from sendanywhere.engine.standard_engine import StandardEngine
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Runner:

    @staticmethod
    def start(script: str) -> None:
        """执行脚本主入口
        """
        now = time.time()
        ymd = time.strftime('%Y-%m-%d', time.localtime(now))
        hms = time.strftime('%H:%M:%S', time.localtime(now))

        log.info(f'START.MS={int(now * 1000)}')
        log.info(f'START.YMD={ymd}')
        log.info(f'START.HMS={hms}')

        # 校验 script脚本不能为空
        if script:
            log.debug(f'script:[ {script} ]')
            Runner.run(script)
        else:
            raise Exception('脚本不允许为空')

    @staticmethod
    def run(script: str) -> None:
        """加载并解析脚本，将脚本反序列化为 HashTree对象
        """
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
    from sendanywhere.utils.path_util import PROJECT_PATH

    # with open(os.path.join(PROJECT_PATH, 'docs', 'http-sampler.json'), 'r', encoding='utf-8') as f:
    # with open(os.path.join(PROJECT_PATH, 'docs', 'test-sampler.json'), 'r', encoding='utf-8') as f:
    with open(os.path.join(PROJECT_PATH, 'docs', 'test-funciton.json'), 'r', encoding='utf-8') as f:
        script = ''.join(f.readlines())
        Runner.start(script)
