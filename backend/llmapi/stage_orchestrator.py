"""
stage_orchestrator.py
=====================

工作目的：
在现有 PromptRunner / SelfValueBot 之上，补一层“阶段桥接层”。

它负责：
1. 承接主对话结果（prompt_result）
2. 基于当前阶段与上下文，抽取 RawStageOutput
3. 驱动 StageLayer 更新阶段状态
4. 处理右侧确认反馈的回流
5. 输出一个后端可继续使用的组合结果
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, List, Optional

from .stage_layer import (
    StageLayer,
    StageState,
    RawStageOutput,
    StageTranslateConfig,
    FeedbackAction,
    build_self_value_method_definition,
)


class StageOrchestrator:
    """
    阶段桥接层
    """

    def __init__(
        self,
        client=None,
        model: Optional[str] = None,
        method_definition=None,
        translate_config: Optional[StageTranslateConfig] = None,
    ):
        self.client = client
        self.model = model
        self.method_definition = method_definition or build_self_value_method_definition()
        self.stage_layer = StageLayer(method_definition=self.method_definition)
        self.translate_config = translate_config or StageTranslateConfig()

    def create_initial_state(self) -> StageState:
        return self.stage_layer.create_initial_stage_state()

    def restore_stage_state(self, state_dict: Optional[Dict[str, Any]]) -> StageState:
        if not state_dict:
            return self.create_initial_state()
        return StageState.from_dict(state_dict)

    def update_after_turn(
        self,
        stage_state: StageState,
        prompt_result: Dict[str, Any],
        answer: str = "",
        qa_history: Optional[List[Dict[str, Any]]] = None,
        mode: str = "self_value",
        conversation_id: str = "",
    ) -> Dict[str, Any]:
        qa_history = qa_history or []

        raw_stage_output = self.extract_raw_stage_output(
            stage_state=stage_state,
            prompt_result=prompt_result,
            answer=answer,
            qa_history=qa_history,
            mode=mode,
        )

        new_stage_state = self.stage_layer.update_stage_state_from_raw_output(
            stage_state=stage_state,
            raw_output=raw_stage_output,
            config=self.translate_config,
        )

        resume_snapshot = None
        if conversation_id:
            resume_snapshot = self.stage_layer.build_resume_snapshot(
                conversation_id=conversation_id,
                stage_state=new_stage_state,
            )

        return {
            "prompt_result": deepcopy(prompt_result),
            "stage_state": new_stage_state.to_dict(),
            "raw_stage_output": raw_stage_output.to_dict(),
            "resume_snapshot": resume_snapshot.to_dict() if resume_snapshot else None,
        }

    def apply_feedback(
        self,
        stage_state: StageState,
        candidate_id: str,
        action: str,
        user_note: str = "",
        conversation_id: str = "",
    ) -> Dict[str, Any]:
        if action not in (
            FeedbackAction.CONFIRMED.value,
            FeedbackAction.REJECTED.value,
            FeedbackAction.REVISED.value,
        ):
            raise ValueError(f"不支持的反馈动作: {action}")

        new_stage_state = self.stage_layer.apply_feedback(
            stage_state=stage_state,
            candidate_id=candidate_id,
            action=action,
            user_note=user_note,
        )

        resume_snapshot = None
        if conversation_id:
            resume_snapshot = self.stage_layer.build_resume_snapshot(
                conversation_id=conversation_id,
                stage_state=new_stage_state,
            )

        return {
            "stage_state": new_stage_state.to_dict(),
            "resume_snapshot": resume_snapshot.to_dict() if resume_snapshot else None,
        }

    def try_transition(self, stage_state: StageState, conversation_id: str = "") -> Dict[str, Any]:
        next_state = self.stage_layer.transition_to_next_stage(stage_state)
        if next_state is None:
            next_state = stage_state

        resume_snapshot = None
        if conversation_id:
            resume_snapshot = self.stage_layer.build_resume_snapshot(
                conversation_id=conversation_id,
                stage_state=next_state,
            )

        return {
            "stage_state": next_state.to_dict(),
            "resume_snapshot": resume_snapshot.to_dict() if resume_snapshot else None,
        }

    def extract_raw_stage_output(
        self,
        stage_state: StageState,
        prompt_result: Dict[str, Any],
        answer: str = "",
        qa_history: Optional[List[Dict[str, Any]]] = None,
        mode: str = "self_value",
    ) -> RawStageOutput:
        qa_history = qa_history or []

        if self.client is None or self.model is None:
            return self._fallback_raw_stage_output(
                stage_state=stage_state,
                prompt_result=prompt_result,
            )

        prompt = self._build_extraction_prompt(
            stage_state=stage_state,
            prompt_result=prompt_result,
            answer=answer,
            qa_history=qa_history,
            mode=mode,
        )

        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content or ""
            return self._parse_raw_stage_output(raw_content)
        except Exception:
            return self._fallback_raw_stage_output(
                stage_state=stage_state,
                prompt_result=prompt_result,
            )

    def _build_extraction_prompt(
        self,
        stage_state: StageState,
        prompt_result: Dict[str, Any],
        answer: str,
        qa_history: List[Dict[str, Any]],
        mode: str,
    ) -> str:
        stage_def = stage_state.stage_definition
        stage_runtime = stage_state.stage_runtime
        snapshot_dict = stage_runtime.stage_snapshot.to_dict() if stage_runtime.stage_snapshot else {}

        qa_tail = qa_history[-6:] if len(qa_history) > 6 else qa_history

        return f"""
你要做的不是继续问答，而是为“当前阶段”抽取一份保守、可运行的阶段原始产出。

当前方法论：
- method_id: {self.method_definition.method_id}
- mode: {mode}

当前阶段定义：
- stage_id: {stage_def.stage_id}
- stage_name: {stage_def.stage_name}
- stage_goal: {stage_def.stage_goal}
- coverage_scope: {stage_def.coverage_scope}
- output_direction: {stage_def.output_direction}

当前阶段运行信息：
- current_maturity: {stage_runtime.current_maturity}
- next_prompt_hint: {stage_runtime.next_prompt_hint}
- current_snapshot: {json.dumps(snapshot_dict, ensure_ascii=False)}

当前用户最新回答：
{answer}

最近 qa_history（截断）：
{json.dumps(qa_tail, ensure_ascii=False)}

当前主对话结果（prompt_result）：
{json.dumps(prompt_result, ensure_ascii=False)}

你的任务：
请只基于“当前阶段”，抽取一份 RawStageOutput。
注意：
1. 不要越阶段推断
2. raw_findings 最多 3 条
3. raw_judgements 最多 2 条
4. 只有当判断被当前阶段材料支持时，才写 raw_judgements
5. 如果当前仍明显处于“继续补材料”，可以不给 raw_judgements
6. 不要为了完整而硬写
7. 输出必须是合法 JSON
8. 不要输出 markdown 代码块

输出格式：
{{
  "stage_summary": "",
  "raw_findings": [],
  "raw_judgements": [],
  "internal_gap_hint": "",
  "next_prompt_hint": ""
}}
""".strip()

    def _parse_raw_stage_output(self, raw_text: str) -> RawStageOutput:
        text = (raw_text or "").strip()

        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        if not (text.startswith("{") and text.endswith("}")):
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                text = text[start:end + 1]

        try:
            data = json.loads(text)
        except Exception:
            return RawStageOutput()

        return RawStageOutput(
            stage_summary=self._clean_text(data.get("stage_summary", "")),
            raw_findings=self._clean_text_list(data.get("raw_findings", []), max_items=3),
            raw_judgements=self._clean_text_list(data.get("raw_judgements", []), max_items=2),
            internal_gap_hint=self._clean_text(data.get("internal_gap_hint", "")),
            next_prompt_hint=self._clean_text(data.get("next_prompt_hint", "")),
        )

    def _fallback_raw_stage_output(
        self,
        stage_state: StageState,
        prompt_result: Dict[str, Any],
    ) -> RawStageOutput:
        summary = self._clean_text(
            prompt_result.get("summary") or prompt_result.get("report") or ""
        )
        next_action = self._clean_text(
            prompt_result.get("next_action") or prompt_result.get("question") or ""
        )

        return RawStageOutput(
            stage_summary=summary[:120],
            raw_findings=[],
            raw_judgements=[],
            internal_gap_hint="",
            next_prompt_hint=next_action[:80],
        )

    def _clean_text(self, text: Any) -> str:
        return str(text or "").strip()

    def _clean_text_list(self, items: Any, max_items: int) -> List[str]:
        if not isinstance(items, list):
            return []
        result: List[str] = []
        for item in items:
            value = self._clean_text(item)
            if value:
                result.append(value)
            if len(result) >= max_items:
                break
        return result
