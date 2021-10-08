# Pymeter

测试脚本执行引擎

## 项目结构

```text
pymeter/
    |-pymeter/
        |-assertions
        |-common
        |-configs
        |-controls
        |-elements
        |-engine
        |-functions
        |-groups
        |-listeners
        |-processors
        |-samplers
        |-timers
        |-utils
    |-config.ini
    |-pytest.ini
    |-pyproject.toml
```


## Snakeviz 分析
- ncalls：调用次数
- tottime：调用该函数中花费的总时间，不包括调用子函数的时间
- percall：tottime / ncalls，每次调用的耗时
- cumtime：在函数中花费的总时间，包括在子函数中的时间
- percall： cumtime / ncalls
- filename:lineno - 函数的位置
