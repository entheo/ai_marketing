"""
prompt_registry.py
==================

工作目的：
统一管理所有原始提示词（raw prompt）及其基础配置。

注意：
1. 这里登记的是 prompt 资源，不是内容状态分类
2. 不要在这里提前把 prompt 写死成 ask / report / plan
3. 模型输出什么状态，由模型在运行时识别
4. 这里的 scene 是“工程包装方式”，不是业务内容判断
"""

from . import prompt_selfvalue as ps


PROMPT_REGISTRY = {
    "self_value.main": {
        # 原始提示词
        "raw_prompt": ps.prompt_self_value_raw,

        # scene 用于 PromptAdapter 选择通用包装方式
        # 这里不是业务状态，而是工程层面的“包装协议类型”
        "scene": "universal",

        # 默认温度，可按需要调整
        "temperature": 1.2,
    },

    # 以后你可以继续加更多原始提示词
    # 例如：
    # "career.explore": {
    #     "raw_prompt": ps.prompt_career_explore_raw,
    #     "scene": "universal",
    #     "temperature": 1.1,
    # },
}
