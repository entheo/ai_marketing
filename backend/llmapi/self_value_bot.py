"""
self_value_bot.py
=================

工作目的：
提供 self_value 业务的轻量调用入口。

当前版本能力：
1. 接入 PromptRunner
2. 接入 StageOrchestrator
3. 普通调用时返回：
   - prompt_result
   - stage_state
   - raw_stage_output
   - resume_snapshot
4. 支持右侧确认反馈回流
5. 支持阶段切换
6. 流式调用时统一输出：
   - message_chunk
   - message_done
   - stage_done

核心思想：
1. SelfValueBot 不再负责硬编码 ask / report / plan 流程
2. SelfValueBot 只负责准备上下文，并调用统一 PromptRunner
3. 内容状态由模型根据上下文自行识别
4. 程序仅通过 PromptRunner 提供轻度护栏
5. 阶段状态由 StageLayer / StageOrchestrator 管理
"""

from typing import Any, Dict, Optional

from .prompt_runner import PromptRunner
from .stage_orchestrator import StageOrchestrator
from .stage_layer import StageState
from .self_value_response_formatter import SelfValueResponseFormatter


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
        self.client = client
        self.model = model
        self.runner = PromptRunner(client=client, model=model)
        self.stage_orchestrator = StageOrchestrator(client=client, model=model)
        self.response_formatter = SelfValueResponseFormatter()

    def _build_context(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建并补全 self_value 默认上下文。

        默认字段：
        - mode
        - round
        - answer
        - qa_history
        - conversation_id
        - stage_state
        """
        context = {
            "mode": "self_value",
            "round": 1,
            "answer": "",
            "qa_history": [],
            "conversation_id": "",
            "stage_state": None,
        }
        context.update(kwargs or {})
        return context

    def _restore_stage_state(self, context: Dict[str, Any]) -> StageState:
        """
        从上下文恢复 stage_state。
        如果没有传入，则初始化。
        """
        stage_state_data = context.get("stage_state")
        return self.stage_orchestrator.restore_stage_state(stage_state_data)

    def self_value_response(self, **kwargs) -> Dict[str, Any]:
        """
        同步调用 self_value 主 prompt，并返回后端组合结果。

        返回：
        {
          "prompt_result": {...},
          "stage_state": {...},
          "raw_stage_output": {...},
          "resume_snapshot": {...}
        }

        注意：
        - 这是后端内部组合结构
        - 如果要给前端直接消费，请再调用 formatter.format_response(...)
        """
        context = self._build_context(kwargs)
        stage_state = self._restore_stage_state(context)

        prompt_result = self.runner.run("self_value.main", **context)

        combined_result = self.stage_orchestrator.update_after_turn(
            stage_state=stage_state,
            prompt_result=prompt_result,
            answer=context.get("answer", ""),
            qa_history=context.get("qa_history", []),
            mode=context.get("mode", "self_value"),
            conversation_id=context.get("conversation_id", ""),
        )

        return combined_result

    def self_value_frontend_response(self, **kwargs) -> Dict[str, Any]:
        """
        同步调用 self_value 主 prompt，并直接返回前端可消费结构。

        返回：
        {
          "message": {...},
          "stage": {...},
          "meta": {...}
        }
        """
        combined_result = self.self_value_response(**kwargs)
        return self.response_formatter.format_response(combined_result)

    def self_value_stream(self, **kwargs):
        """
        流式调用 self_value 主 prompt。

        统一事件协议：
        - message_chunk: 左侧原始流式文本
        - message_done: 左侧最终结构化结果（与普通接口 message 结构一致）
        - stage_done: 右侧阶段结果（stage + meta）
        - error: 错误事件
        """
        context = self._build_context(kwargs)
        stage_state = self._restore_stage_state(context)

        final_prompt_result: Optional[Dict[str, Any]] = None

        for item in self.runner.stream("self_value.main", **context):
            event = item.get("event")

            if event == "chunk":
                yield {
                    "event": "message_chunk",
                    "content": item.get("content", "")
                }

            elif event == "done":
                final_prompt_result = item.get("data")

                if not isinstance(final_prompt_result, dict):
                    yield {
                        "event": "error",
                        "message": "PromptRunner stream done event missing valid data."
                    }
                    return

                combined_result = self.stage_orchestrator.update_after_turn(
                    stage_state=stage_state,
                    prompt_result=final_prompt_result,
                    answer=context.get("answer", ""),
                    qa_history=context.get("qa_history", []),
                    mode=context.get("mode", "self_value"),
                    conversation_id=context.get("conversation_id", ""),
                )

                formatted_result = self.response_formatter.format_response(combined_result)

                yield {
                    "event": "message_done",
                    "data": formatted_result.get("message", {})
                }

                yield {
                    "event": "stage_done",
                    "data": {
                        "stage": formatted_result.get("stage", {}),
                        "meta": formatted_result.get("meta", {}),
                    }
                }

            elif event == "error":
                yield item

    def apply_stage_feedback(
        self,
        candidate_id: str,
        action: str,
        user_note: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        处理右侧确认反馈。

        action 支持：
        - confirmed
        - rejected
        - revised

        返回后端组合结果：
        {
          "stage_state": {...},
          "resume_snapshot": {...}
        }
        """
        context = self._build_context(kwargs)
        stage_state = self._restore_stage_state(context)

        return self.stage_orchestrator.apply_feedback(
            stage_state=stage_state,
            candidate_id=candidate_id,
            action=action,
            user_note=user_note,
            conversation_id=context.get("conversation_id", ""),
        )

    def apply_stage_feedback_frontend(
        self,
        candidate_id: str,
        action: str,
        user_note: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        处理右侧确认反馈，并直接返回前端可消费结构。

        返回：
        {
          "stage": {...},
          "meta": {...}
        }
        """
        feedback_result = self.apply_stage_feedback(
            candidate_id=candidate_id,
            action=action,
            user_note=user_note,
            **kwargs,
        )

        stage_state = feedback_result.get("stage_state") or {}
        resume_snapshot = feedback_result.get("resume_snapshot") or {}

        return {
            "stage": self.response_formatter._build_stage_block(stage_state),
            "meta": self.response_formatter._build_meta_block(stage_state, resume_snapshot),
        }

    def try_stage_transition(self, **kwargs) -> Dict[str, Any]:
        """
        尝试切换到下一阶段。

        返回后端组合结果：
        {
          "stage_state": {...},
          "resume_snapshot": {...}
        }
        """
        context = self._build_context(kwargs)
        stage_state = self._restore_stage_state(context)

        return self.stage_orchestrator.try_transition(
            stage_state=stage_state,
            conversation_id=context.get("conversation_id", ""),
        )

    def try_stage_transition_frontend(self, **kwargs) -> Dict[str, Any]:
        """
        尝试切换到下一阶段，并直接返回前端可消费结构。

        返回：
        {
          "stage": {...},
          "meta": {...}
        }
        """
        transition_result = self.try_stage_transition(**kwargs)

        stage_state = transition_result.get("stage_state") or {}
        resume_snapshot = transition_result.get("resume_snapshot") or {}

        return {
            "stage": self.response_formatter._build_stage_block(stage_state),
            "meta": self.response_formatter._build_meta_block(stage_state, resume_snapshot),
        }
