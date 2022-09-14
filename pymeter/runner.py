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
from pymeter.utils.json_util import to_json
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Runner:

    @staticmethod
    def start(
            script: str or list,
            throw_ex: bool = False,
            use_sio_log_handler: bool = False,
            ext: dict = None,
            plugins=None
    ) -> None:
        """执行脚本的入口

        Args:
            script:                 脚本
            throw_ex:               是否抛出异常
            use_sio_log_handler:    是否使用 socket 实时传递运行时日志
            ext:                    外部扩展，用于传递外部对象
            plugins:                插件

        Returns:

        """
        # 校验 script脚本不能为空
        if not script:
            raise Exception('脚本不允许为空')

        if use_sio_log_handler:
            if 'sio' not in ext or 'sid' not in ext:
                raise Exception('使用 ExternalSocketIOHandler 时，ext 参数中 sio 和 sid 不能为空')
            log_util.EXTERNAL_SOCKET_IO_HANDLER.LOCAL.sio = ext.get('sio')
            log_util.EXTERNAL_SOCKET_IO_HANDLER.LOCAL.sid = ext.get('sid')

        log.debug(f'script:\n{to_json(script)}')

        # noinspection PyBroadException
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
        engine.run_test()


if __name__ == '__main__':
    import cProfile
    import os

    from pymeter import config as CONFIG

    # file = 'http-sampler.json'
    # file = 'while-controller.json'
    # file = 'http-session-manager.json'
    # file = 'transaction-listener.json'
    # file = 'transaction-http-session-manager.json'
    file = 'debug.json'

    with open(os.path.join(CONFIG.PROJECT_PATH, 'scripts', file), 'r', encoding='utf-8') as f:
        debug_script = ''.join(f.readlines())
        # cProfile.run('Runner.start(script)', filename='profile.out')
        Runner.start(debug_script)
