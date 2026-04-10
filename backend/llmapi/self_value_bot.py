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

import random
import re
import time
import os
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
        self.recent_window_rounds = max(1, int(os.getenv("SELF_VALUE_RECENT_WINDOW_ROUNDS", "6")))
        self.long_term_summary_max_chars = max(120, int(os.getenv("SELF_VALUE_LONG_TERM_SUMMARY_MAX_CHARS", "500")))
        self.summary_refresh_rounds = max(1, int(os.getenv("SELF_VALUE_SUMMARY_REFRESH_ROUNDS", "2")))

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
            "dialog_mode": "raw_coach_extreme",
            "round": 1,
            "answer": "",
            "qa_history": [],
            "qa_history_summary": "",
            "conversation_id": "",
            "stage_state": None,
        }
        context.update(kwargs or {})
        return context

    def _is_initialization_turn(self, context: Dict[str, Any]) -> bool:
        round_num = self._safe_round(context)
        answer = str(context.get("answer") or "").strip()
        qa_history = context.get("qa_history", [])
        return round_num <= 1 and not answer and (not isinstance(qa_history, list) or len(qa_history) == 0)

    def _get_initialization_question(self) -> str:
        return "回顾过去5年，哪件事你做得比大多数人轻松，且结果出色？（即使你觉得'这很简单'）"

    def _build_initialization_frontend_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        stage_state_obj = self.stage_orchestrator.create_initial_state()
        stage_state = stage_state_obj.to_dict()
        resume_snapshot = None
        conversation_id = str(context.get("conversation_id") or "").strip()

        if conversation_id:
            snapshot_obj = self.stage_orchestrator.stage_layer.build_resume_snapshot(  # noqa: SLF001
                conversation_id=conversation_id,
                stage_state=stage_state_obj,
            )
            resume_snapshot = snapshot_obj.to_dict()

        question = self._get_initialization_question()
        message = {
            "status": "ask",
            "question_type": "text",
            "question": question,
            "options": [],
            "summary": "",
            "report": "",
            "next_action": "",
            "question_length_hint": "long" if len(question) > 30 else "medium",
            "should_end": False,
            "can_summarize": False,
        }

        return {
            "message": message,
            "stage": self.response_formatter._build_stage_block(stage_state),  # noqa: SLF001
            "meta": self.response_formatter._build_meta_block(stage_state, resume_snapshot),  # noqa: SLF001
            "stage_state": stage_state,
            "candidate_insight": "",
            "candidate_id": "",
            "confirmed_insight": "",
        }

    def _truncate_text(self, text: Any, max_chars: int) -> str:
        value = str(text or "").strip()
        if len(value) <= max_chars:
            return value
        return value[:max_chars].rstrip("，。、；：,.;: ") + "…"

    def _safe_round(self, context: Dict[str, Any]) -> int:
        try:
            return int(context.get("round", 1))
        except (TypeError, ValueError):
            return 1

    def _build_identity_kernel(self) -> str:
        return (
            "你是个人商业模式咨询教练。"
            "保持阶段推进，同时用自然对话方式探索。"
            "优先承接用户表达，避免机械复述规则。"
        )

    def _sanitize_qa_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        answer = self._truncate_text(item.get("answer", ""), 220)
        return {
            "round": item.get("round", ""),
            "answer": answer,
            "user_signal": self._truncate_text(answer, 72),
        }

    def _build_recent_qa_window(self, qa_history: Any) -> list:
        if not isinstance(qa_history, list):
            return []
        tail = qa_history[-self.recent_window_rounds:] if len(qa_history) > self.recent_window_rounds else qa_history
        result = []
        for item in tail:
            if isinstance(item, dict):
                result.append(self._sanitize_qa_item(item))
        return result

    def _extract_stage_memory(self, stage_state: Any) -> Dict[str, Any]:
        if not isinstance(stage_state, dict):
            return {}

        stage_def = stage_state.get("stage_definition") or {}
        stage_runtime = stage_state.get("stage_runtime") or {}
        snapshot = stage_runtime.get("stage_snapshot") or {}

        findings = []
        for item in (snapshot.get("findings") or [])[:3]:
            if isinstance(item, dict):
                text = self._truncate_text(item.get("content", ""), 64)
                if text:
                    findings.append(text)

        judgements = []
        for item in (snapshot.get("judgements") or [])[:2]:
            if isinstance(item, dict):
                text = self._truncate_text(item.get("content", ""), 80)
                if text:
                    judgements.append(text)

        return {
            "current_stage_id": stage_def.get("stage_id", ""),
            "current_stage_name": stage_def.get("stage_name", ""),
            "current_maturity": stage_runtime.get("current_maturity", ""),
            "can_transition": bool(stage_runtime.get("can_transition", False)),
            "stage_summary": self._truncate_text(snapshot.get("stage_summary", ""), 120),
            "findings": findings,
            "judgements": judgements,
        }

    def _extract_high_confidence_memory(self, stage_state: Any) -> Dict[str, Any]:
        if not isinstance(stage_state, dict):
            return {"confirmed": [], "rejected_or_questioned": []}

        stage_runtime = stage_state.get("stage_runtime") or {}
        snapshot = stage_runtime.get("stage_snapshot") or {}
        confirmed = []
        rejected_or_questioned = []

        for item in (snapshot.get("judgements") or []):
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "") or "").strip().lower()
            text = self._truncate_text(item.get("content", ""), 88)
            if not text:
                continue
            if status == "confirmed":
                confirmed.append(text)
            elif status in ("questioned", "rejected", "under_revision"):
                rejected_or_questioned.append(text)

        return {
            "confirmed": confirmed[:3],
            "rejected_or_questioned": rejected_or_questioned[:3],
        }

    def _build_long_term_memory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        stage_state = context.get("stage_state")
        confidence = self._extract_high_confidence_memory(stage_state)
        summary = self._truncate_text(context.get("qa_history_summary", ""), 180)

        memory = {
            "confirmed": confidence["confirmed"],
            "rejected_or_questioned": confidence["rejected_or_questioned"],
            "history_summary": "",
        }

        if summary:
            memory["history_summary"] = summary
        return memory

    def _build_runner_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        runner_context = dict(context)
        recent_window = self._build_recent_qa_window(context.get("qa_history", []))
        stage_memory = self._extract_stage_memory(context.get("stage_state"))
        long_term_memory = self._build_long_term_memory(context)

        runner_context["qa_history"] = recent_window
        runner_context["identity_kernel"] = self._build_identity_kernel()
        runner_context["stage_memory"] = stage_memory
        runner_context["long_term_memory"] = long_term_memory
        return runner_context

    def _restore_stage_state(self, context: Dict[str, Any]) -> StageState:
        """
        从上下文恢复 stage_state。
        如果没有传入，则初始化。
        """
        stage_state_data = context.get("stage_state")
        return self.stage_orchestrator.restore_stage_state(stage_state_data)

    def _normalize_pending_candidate(self, context: Dict[str, Any]) -> Dict[str, str]:
        pending = context.get("pending_insight_candidate")
        if not isinstance(pending, dict):
            return {}

        candidate_id = str(pending.get("candidate_id") or "").strip()
        text = str(pending.get("text") or "").strip()

        if not candidate_id or not text:
            return {}
        return {
            "candidate_id": candidate_id,
            "text": text,
        }

    def _is_explicit_confirmation(self, answer: str) -> bool:
        text = str(answer or "").strip()
        if not text:
            return False

        normalized = re.sub(r"\s+", "", text.lower())
        deny_tokens = (
            "不是", "不对", "不太对", "没说中", "没感觉", "不认同", "不认可", "并不", "但", "不过", "然而"
        )
        if any(token in normalized for token in deny_tokens):
            return False

        confirm_tokens = (
            "是的", "对的", "对", "没错", "说得对", "你说得准", "很准", "准确", "认同", "认可", "贴近", "就是这个", "确实", "说到点子上"
        )
        return any(token in normalized for token in confirm_tokens)

    def _extract_candidate_insight(self, prompt_result: Dict[str, Any]) -> str:
        for key in ("candidate_insight", "insight"):
            value = str(prompt_result.get(key) or "").strip()
            if value:
                return value

        # 兼容当前 self_value 主链路：多数情况下只有 summary/question，没有显式 candidate_insight。
        summary_text = str(prompt_result.get("summary") or "").strip()
        if summary_text:
            return summary_text

        question_text = str(prompt_result.get("question") or "").strip()
        if not question_text:
            return ""

        # 优先提取问句前的判断性短句，避免把整段问题当 insight。
        parts = re.split(r"[。！？!?]", question_text)
        for part in parts:
            candidate = part.strip(" ，,；;：:")
            if len(candidate) < 8:
                continue
            if "?" in candidate or "？" in candidate:
                continue
            if "你" not in candidate:
                continue
            return candidate

        return ""

    def _build_insight_signal(
        self,
        prompt_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, str]:
        pending = self._normalize_pending_candidate(context)
        answer = str(context.get("answer") or "")

        if pending and self._is_explicit_confirmation(answer):
            return {
                "confirmed_insight": pending["text"],
                "candidate_insight": "",
                "candidate_id": "",
            }

        candidate_text = self._extract_candidate_insight(prompt_result)
        if not candidate_text:
            return {
                "candidate_insight": "",
                "candidate_id": "",
                "confirmed_insight": "",
            }

        candidate_id = str(prompt_result.get("candidate_id") or "").strip()
        if not candidate_id:
            candidate_id = f"cand_{int(time.time() * 1000)}_{random.randint(100, 999)}"
        return {
            "candidate_insight": candidate_text,
            "candidate_id": candidate_id,
            "confirmed_insight": "",
        }

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
        runner_context = self._build_runner_context(context)

        prompt_result = self.runner.run("self_value.main", **runner_context)

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
        context = self._build_context(kwargs)
        if self._is_initialization_turn(context):
            return self._build_initialization_frontend_response(context)

        combined_result = self.self_value_response(**kwargs)
        formatted = self.response_formatter.format_response(combined_result)
        formatted.update(
            self._build_insight_signal(
                prompt_result=combined_result.get("prompt_result") or {},
                context=context,
            )
        )
        return formatted

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
        if self._is_initialization_turn(context):
            payload = self._build_initialization_frontend_response(context)
            yield {
                "event": "message_done",
                "data": {
                    **(payload.get("message") or {}),
                    "candidate_insight": "",
                    "candidate_id": "",
                    "confirmed_insight": "",
                }
            }
            yield {
                "event": "stage_done",
                "data": {
                    "stage": payload.get("stage") or {},
                    "meta": payload.get("meta") or {},
                    "stage_state": payload.get("stage_state") or {},
                }
            }
            return

        stage_state = self._restore_stage_state(context)
        runner_context = self._build_runner_context(context)

        final_prompt_result: Optional[Dict[str, Any]] = None

        for item in self.runner.stream("self_value.main", **runner_context):
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

                # 先快速回传左侧消息，尽量缩短输入解锁等待时间。
                fast_message = self.response_formatter._build_message_block(final_prompt_result)  # noqa: SLF001
                insight_signal = self._build_insight_signal(
                    prompt_result=final_prompt_result or {},
                    context=context,
                )
                yield {
                    "event": "message_done",
                    "data": {
                        **fast_message,
                        **insight_signal,
                    }
                }

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
                    "event": "stage_done",
                    "data": {
                        "stage": formatted_result.get("stage", {}),
                        "meta": formatted_result.get("meta", {}),
                        "stage_state": formatted_result.get("stage_state"),
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
