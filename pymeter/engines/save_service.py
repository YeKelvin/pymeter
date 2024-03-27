#!/usr/bin python3
# @File    : save_service.py
# @Time    : 2023-07-31 10:53:10
# @Author  : Kelvin.Ye


modules = {
    # 测试集合
    'TestCollection': 'pymeter.collections.test_collection',

    # 工作线程
    'TestWorker': 'pymeter.workers.test_worker',
    'SetupWorker': 'pymeter.workers.setup_worker',
    'TeardownWorker': 'pymeter.workers.teardown_worker',

    # 配置器
    'Arguments': 'pymeter.configs.arguments',
    'Argument': 'pymeter.configs.arguments',
    'HTTPArgument': 'pymeter.configs.httpconfigs',
    'HTTPFileArgument': 'pymeter.configs.httpconfigs',
    'HTTPHeader': 'pymeter.configs.httpconfigs',
    'HTTPHeaderManager': 'pymeter.configs.httpconfigs',
    'HTTPCookieManager': 'pymeter.configs.httpconfigs',
    'HTTPSessionManager': 'pymeter.configs.httpconfigs',
    'TransactionParameter': 'pymeter.configs.transactions',
    'TransactionHTTPSessionManager': 'pymeter.configs.transactions',
    'VariableDataset': 'pymeter.configs.dataset',
    'DatabaseEngine': 'pymeter.configs.database',

    # 逻辑控制器
    'IfController': 'pymeter.controls.if_controller',
    'LoopController': 'pymeter.controls.loop_controller',
    'WhileController': 'pymeter.controls.while_controller',
    'ForeachController': 'pymeter.controls.foreach_controller',
    'RetryController': 'pymeter.controls.retry_controller',
    'TransactionController': 'pymeter.controls.transaction',

    # 时间控制器
    'ConstantTimer': 'pymeter.timers.constant_timer',

    # 取样器
    'SQLSampler': 'pymeter.samplers.sql_sampler',
    'HTTPSampler': 'pymeter.samplers.http_sampler',
    'PythonSampler': 'pymeter.samplers.python_sampler',

    # 前置处理器
    'SleepPrevProcessor': 'pymeter.processors.sleep_prev_processor',
    'PythonPrevProcessor': 'pymeter.processors.python_prev_processor',

    # 后置处理器
    'SleepPostProcessor': 'pymeter.processors.sleep_post_processor',
    'PythonPostProcessor': 'pymeter.processors.python_post_processor',
    'JsonPathPostProcessor': 'pymeter.processors.jsonpath_post_processor',

    # 断言器
    'PythonAssertion': 'pymeter.assertions.python_test_assertion',
    'JsonPathAssertion': 'pymeter.assertions.jsonpath_test_assertion',

    # 监听器
    'ResultCollector': 'pymeter.listeners.result_collector',
    'FlaskDBResultStorage': 'pymeter.listeners.flask_db_result_storage',
    'FlaskDBIterationStorage': 'pymeter.listeners.flask_db_iteration_storage',
    'FlaskSIOResultCollector': 'pymeter.listeners.flask_sio_result_collector',
    'SocketResultCollector': 'pymeter.listeners.socket_result_collector'
}
