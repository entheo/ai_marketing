"""
self_value_bot.py
=================

工作目的：
提供 self_value 业务的轻量调用入口。

核心思想：
1. SelfValueBot 不再负责硬编码 ask / report / plan 流程
2. SelfValueBot 只负责准备上下文，并调用统一 PromptRunner
3. 内容状态由模型根据上下文自行识别
4. 程序仅通过 PromptRunner 提供轻度护栏
"""

from .prompt_runner import PromptRunner


class SelfValueBot:
    """
    self_value 业务入口类
    """

    def __init__(self, client=None, model=None):
        """
        初始化 SelfValueBot

        参数：
        - client: 大模型客户端
        - model: 模型名称
        """
        self.runner = PromptRunner(client=client, model=model)

    def _build_context(self, kwargs):
        """
        构建并补全 self_value 默认上下文。

        默认字段：
        - mode
        - round
        - answer
        - qa_history
        """
        context = {
            "mode": "self_value",
            "round": 1,
            "answer": "",
            "qa_history": [],
        }
        context.update(kwargs or {})
        return context

    def self_value_response(self, **kwargs):
        """
        同步调用 self_value 主 prompt。

        使用方式：
            bot.self_value_response(
                round=2,
                answer="我最不能接受被低估",
                qa_history=[...]
            )

        返回：
        - 标准化结构化 JSON
        """
        context = self._build_context(kwargs)
        return self.runner.run("self_value.main", **context)

    def self_value_stream(self, **kwargs):
        """
        流式调用 self_value 主 prompt。

        返回事件：
        - chunk: 原始流式文本片段
        - done: 最终结构化结果
        - error: 错误事件
        """
        context = self._build_context(kwargs)
        for item in self.runner.stream("self_value.main", **context):
            yield item
