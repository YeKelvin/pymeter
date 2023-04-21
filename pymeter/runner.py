#!/usr/bin python3
# @File    : runner.py
# @Time    : 2020/2/12 11:46
# @Author  : Kelvin.Ye
import time

from loguru import logger
from loguru._logger import context as logurucontext

from pymeter.engine import script_server
from pymeter.engine.standard_engine import StandardEngine
from pymeter.tools.exceptions import InvalidScriptException
from pymeter.utils.json_util import to_json
from pymeter.utils.log_util import SocketIOHandler


class Runner:

    @staticmethod
    def start(
            script: str or list,
            throw_ex: bool = False,
            extra: dict = None,
            plugins=None
    ) -> None:
        """执行脚本的入口

        Args:
            script:    脚本
            throw_ex:  是否抛出异常
            extra:     外部扩展，用于传递外部对象
            plugins:   插件

        """
        # 校验 script脚本不能为空
        if not script:
            raise InvalidScriptException('脚本不允许为空')

        if 'sio' in extra and 'sid' in extra:
            handler_id = logger.add(
                SocketIOHandler(extra.get('sio'), extra.get('sid')),
                level='INFO',
                format='[{time:%Y-%m-%d %H:%M:%S.%f}] [{level}] {message}'
            )

        # log注入traceid和sid
        logurucontext.set({
            **logurucontext.get(),
            'traceid': extra.get('traceid'),
            'sid': extra.get('sid')
        })

        # noinspection PyBroadException
        try:
            logger.debug(f'script:\n{to_json(script)}')
            Runner.run(script, extra)
        except Exception:
            logger.exception()
            if throw_ex:
                raise
        finally:
            logger.remove(handler_id)

    @staticmethod
    def run(script: str, extra=None) -> None:
        """加载并解析脚本，将脚本反序列化为 HashTree对象"""
        now = time.time()
        ymd = time.strftime('%Y-%m-%d', time.localtime(now))
        hms = time.strftime('%H:%M:%S', time.localtime(now))

        # 加载脚本
        hashtree = script_server.load_tree(script)
        logger.debug(f'hashtree:\n{hashtree}')

        # 将脚本配置到执行引擎中
        engine = StandardEngine(
            extra=extra,
            props={
                'START.MS': int(now * 1000),
                'START.YMD': ymd,
                'START.HMS': hms
            }
        )
        engine.configure(hashtree)

        # 开始执行测试
        engine.run_test()


if __name__ == '__main__':
    # import cProfile
    import os
    import sys

    logger.add(
        sys.stdout,
        level='DEBUG',
        colorize=True,
        format='<green>[{time:%Y-%m-%d %H:%M:%S.%f}]</green> <level>[{level}] [{module}:{function}:{line}] {message}</level>'
    )

    # file = 'http-sampler.json'
    # file = 'while-controller.json'
    # file = 'http-session-manager.json'
    # file = 'transaction-listener.json'
    # file = 'transaction-http-session-manager.json'
    file = 'debug.json'

    with open(os.path.join('../scripts', file), encoding='utf-8') as f:
        debug_script = ''.join(f.readlines())
        # cProfile.run('Runner.start(script)', filename='profile.out')
        Runner.start(debug_script)
