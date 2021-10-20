#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : runner.py
# @Time    : 2020/2/12 11:46
# @Author  : Kelvin.Ye
import time
import traceback

from pymeter.engine import script_server
from pymeter.engine.standard_engine import StandardEngine
from pymeter.utils import log_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Runner:

    @staticmethod
    def start(script: str or list, throw_ex: bool = False, sio=None, sid=None, ext=None, plugins=None) -> None:
        """执行脚本的入口

        Args:
            script:     脚本
            throw_ex:   是否抛出异常
            sio:        SocketIO实例
            sid:        用户sid
            ext:        外部扩展字典，用于传递外部对象
            plugins:    插件

        Returns:

        """
        # 校验 script脚本不能为空
        if not script:
            raise Exception('脚本不允许为空')

        if sio and sid:
            log_util.SOCKET_IO_HANDLER.LOCAL.sio = sio
            log_util.SOCKET_IO_HANDLER.LOCAL.sid = sid

        # log.debug(f'script:\n{script}')
        try:
            Runner.run(script, ext)
        except Exception:
            log.error(traceback.format_exc())
            if throw_ex:
                raise

    @staticmethod
    def run(script: str, ext=None) -> None:
        """加载并解析脚本，将脚本反序列化为 HashTree对象"""
        now = time.time()
        ymd = time.strftime('%Y-%m-%d', time.localtime(now))
        hms = time.strftime('%H:%M:%S', time.localtime(now))

        # 加载脚本
        hashtree = script_server.load_tree(script)
        log.debug(f'script hashtree:\n{hashtree}')

        # 将脚本配置到执行引擎中
        engine = StandardEngine(props={
            'START.MS': int(now * 1000),
            'START.YMD': ymd,
            'START.HMS': hms
        })
        engine.configure(hashtree)

        # 开始执行测试
        log.info('开始执行测试')
        engine.run_test()


if __name__ == '__main__':
    import cProfile
    import os

    from pymeter.utils.path_util import PROJECT_PATH

    # script = 'http-sampler.json'
    # script = 'while-controller.json'
    # script = 'http-session-manager.json'
    # script = 'transaction-listener.json'
    # script = 'transaction-http-session-manager.json'
    script = 'debug.json'

    with open(os.path.join(PROJECT_PATH, 'scripts', script), 'r', encoding='utf-8') as f:
        script = ''.join(f.readlines())
        # cProfile.run('Runner.start(script)', filename='profile.out')
        Runner.start(script)
