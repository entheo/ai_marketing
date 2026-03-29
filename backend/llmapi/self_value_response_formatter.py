"""
self_value_response_formatter.py
================================

工作目的：
把 SelfValueBot 当前返回的组合结果，整理成前端更易消费的统一响应结构。

输入：
{
  "prompt_result": {...},
  "stage_state": {...},
  "raw_stage_output": {...},
  "resume_snapshot": {...}
}

输出：
{
  "message": {...},
  "stage": {...},
  "meta": {...},
  "stage_state": {...}
}

设计原则：
1. 左侧主对话只看 message
2. 右侧阶段成果区只看 stage
3. 页面流程控制只看 meta
4. 前端额外缓存 stage_state，供后续接口原样回传
5. 不把 raw_stage_output 暴露给前端
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


class SelfValueResponseFormatter:
    """
    SelfValue 响应整形器
    """

    def format_response(self, combined_result: Dict[str, Any]) -> Dict[str, Any]:
        prompt_result = deepcopy(combined_result.get("prompt_result") or {})
        stage_state = deepcopy(combined_result.get("stage_state") or {})
        resume_snapshot = deepcopy(combined_result.get("resume_snapshot") or {})

        return {
            "message": self._build_message_block(prompt_result),
            "stage": self._build_stage_block(stage_state),
            "meta": self._build_meta_block(stage_state, resume_snapshot),
            "stage_state": stage_state,  # 原样透传，前端只缓存，不直接展示
        }

    # =========================
    # 左侧主对话区
    # =========================

    def _build_message_block(self, prompt_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": self._text(prompt_result.get("status")),
            "question_type": self._text(prompt_result.get("question_type")),
            "question": self._text(prompt_result.get("question")),
            "options": self._list(prompt_result.get("options")),
            "summary": self._text(prompt_result.get("summary")),
            "report": self._text(prompt_result.get("report")),
            "next_action": self._text(prompt_result.get("next_action")),
            "question_length_hint": self._text(prompt_result.get("question_length_hint")),
            "should_end": bool(prompt_result.get("should_end", False)),
            "can_summarize": bool(prompt_result.get("can_summarize", False)),
        }

    # =========================
    # 右侧阶段成果区
    # =========================

    def _build_stage_block(self, stage_state: Dict[str, Any]) -> Dict[str, Any]:
        stage_definition = stage_state.get("stage_definition") or {}
        stage_runtime = stage_state.get("stage_runtime") or {}
        stage_snapshot = stage_runtime.get("stage_snapshot") or {}

        return {
            "stage_id": self._text(stage_definition.get("stage_id")),
            "stage_name": self._text(stage_definition.get("stage_name")),
            "stage_goal": self._text(stage_definition.get("stage_goal")),
            "coverage_scope": self._list(stage_definition.get("coverage_scope")),
            "output_direction": self._list(stage_definition.get("output_direction")),
            "stage_summary": self._text(stage_snapshot.get("stage_summary")),
            "findings": self._normalize_stage_items(stage_snapshot.get("findings")),
            "judgements": self._normalize_judgements(stage_snapshot.get("judgements")),
            "confirmation_candidates": self._normalize_confirmation_candidates(
                stage_snapshot.get("confirmation_candidates")
            ),
            "next_prompt_hint": self._text(stage_snapshot.get("next_prompt_hint")),
        }

    def _normalize_stage_items(self, items: Any) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []

        result: List[Dict[str, Any]] = []
        for item in items:
            item = item or {}
            result.append(
                {
                    "id": self._text(item.get("id")),
                    "content": self._text(item.get("content")),
                    "status": self._text(item.get("status")),
                }
            )
        return result

    def _normalize_judgements(self, items: Any) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []

        result: List[Dict[str, Any]] = []
        for item in items:
            item = item or {}
            result.append(
                {
                    "id": self._text(item.get("id")),
                    "content": self._text(item.get("content")),
                    "status": self._text(item.get("status")),
                    "supported_by": self._list(item.get("supported_by")),
                }
            )
        return result

    def _normalize_confirmation_candidates(self, items: Any) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []

        result: List[Dict[str, Any]] = []
        for item in items:
            item = item or {}
            result.append(
                {
                    "id": self._text(item.get("id")),
                    "source_judgement_id": self._text(item.get("source_judgement_id")),
                    "content": self._text(item.get("content")),
                    "impact": self._text(item.get("impact")),
                    "status": self._text(item.get("status")),
                    "user_note": self._text(item.get("user_note")),
                }
            )
        return result

    # =========================
    # 页面流程控制 / 恢复信息
    # =========================

    def _build_meta_block(
        self,
        stage_state: Dict[str, Any],
        resume_snapshot: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        stage_definition = stage_state.get("stage_definition") or {}
        stage_runtime = stage_state.get("stage_runtime") or {}
        stage_snapshot = stage_runtime.get("stage_snapshot") or {}
        resume_snapshot = resume_snapshot or {}

        return {
            "method_id": self._text(
                resume_snapshot.get("method_id") or stage_snapshot.get("method_id")
            ),
            "conversation_id": self._text(resume_snapshot.get("conversation_id")),
            "current_stage_id": self._text(
                resume_snapshot.get("current_stage_id") or stage_definition.get("stage_id")
            ),
            "current_stage_name": self._text(stage_definition.get("stage_name")),
            "current_maturity": self._text(
                resume_snapshot.get("current_stage_maturity") or stage_runtime.get("current_maturity")
            ),
            "can_transition": bool(stage_runtime.get("can_transition", False)),
            "has_blocking_confirmation": bool(
                stage_runtime.get("has_blocking_confirmation", False)
                or resume_snapshot.get("has_blocking_pending_confirmation", False)
            ),
            "stage_status": self._text(stage_runtime.get("status")),
            "last_feedback_event": deepcopy(stage_runtime.get("last_feedback_event")),
            "resume_snapshot": deepcopy(resume_snapshot) if resume_snapshot else None,
        }

    # =========================
    # 工具方法
    # =========================

    def _text(self, value: Any) -> str:
        return "" if value is None else str(value)

    def _list(self, value: Any) -> List[Any]:
        return value if isinstance(value, list) else []
