"""
prompt_runner.py
================

工作目的：
统一执行 prompt 的运行流程。

它负责：
1. 从注册表读取 raw prompt
2. 使用 PromptAdapter 编译完整 prompt
3. 调用大模型
4. 解析 JSON 结果
5. 对模型返回做轻度流程护栏
6. 返回前端可直接使用的统一结构
7. 对不合格输出进行基础修复与必要重写

它不负责：
1. 预先替模型决定业务状态
2. 把 prompt 强行绑定为 ask / report / plan
"""

import json
from typing import Any, Dict

from .prompt_adapter import PromptAdapter
from .prompt_registry import PROMPT_REGISTRY


class PromptRunner:
    """
    统一 Prompt 执行器
    """

    def __init__(self, client=None, model=None):
        """
        初始化执行器

        参数：
        - client: 大模型客户端
        - model: 模型名称
        """
        self.client = client
        self.model = model

        self.min_summary_round = 4
        self.force_summary_round = 8
        self.max_rewrite_attempts = 1

    def get_messages(self, rendered_prompt: str):
        """
        构建 messages。
        """
        return [
            {
                "role": "user",
                "content": rendered_prompt
            }
        ]

    def _safe_round(self, context: Dict[str, Any]) -> int:
        """
        安全读取 round，避免 round 类型异常导致报错。
        """
        try:
            return int(context.get("round", 1))
        except (TypeError, ValueError):
            return 1

    def _extract_json_text(self, raw_text: str) -> str:
        """
        尝试从模型返回中提取 JSON 字符串。
        """
        text = (raw_text or "").strip()

        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        if text.startswith("{") and text.endswith("}"):
            return text

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]

        return text

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """
        解析模型返回的 JSON。
        """
        json_text = self._extract_json_text(raw_text)

        try:
            return json.loads(json_text)
        except Exception as e:
            return {
                "status": "error",
                "question_type": "",
                "question": "",
                "options": [],
                "summary": f"JSON 解析失败: {str(e)}",
                "report": "",
                "next_action": "",
                "question_length_hint": "",
                "should_end": False,
                "can_summarize": False,
                "raw_content": raw_text,
            }

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一补全输出字段，避免前端因为字段缺失而出错。
        """
        normalized = dict(result or {})

        normalized.setdefault("status", "error")
        normalized.setdefault("question_type", "")
        normalized.setdefault("question", "")
        normalized.setdefault("options", [])
        normalized.setdefault("summary", "")
        normalized.setdefault("report", "")
        normalized.setdefault("next_action", "")
        normalized.setdefault("question_length_hint", "")
        normalized.setdefault("should_end", False)
        normalized.setdefault("can_summarize", False)

        if not isinstance(normalized.get("options"), list):
            normalized["options"] = []

        normalized["should_end"] = bool(normalized.get("should_end", False))
        normalized["can_summarize"] = bool(normalized.get("can_summarize", False))

        # 兼容旧输出：open -> text
        if normalized.get("question_type") == "open":
            normalized["question_type"] = "text"

        for key in (
            "status",
            "question_type",
            "question",
            "summary",
            "report",
            "next_action",
            "question_length_hint",
        ):
            value = normalized.get(key, "")
            normalized[key] = "" if value is None else str(value)

        return normalized

    def _calc_question_length_hint(self, question: str) -> str:
        """
        根据问题长度推导展示提示。
        """
        length = len((question or "").strip())
        if length == 0:
            return ""
        if length <= 20:
            return "short"
        if length <= 30:
            return "medium"
        return "long"

    def _trim_question_if_needed(self, question: str) -> str:
        """
        极端兜底：
        如果问题异常长，先做非常轻度的本地裁剪。
        """
        question = (question or "").strip().replace("\n", "").replace("\r", "")
        if len(question) <= 36:
            return question

        trimmed = question[:36].rstrip("，。、；：,.;: ")
        if not trimmed.endswith(("？", "?")):
            trimmed += "？"
        return trimmed

    def _repair_shape(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据 status 修复结构，确保返回更稳定。
        """
        status = result.get("status", "")
        question_type = result.get("question_type", "")
        options = result.get("options", [])

        if status in ("ask", "clarify"):
            if question_type == "single_choice":
                if not isinstance(options, list) or len(options) < 2:
                    result["options"] = ["选项一", "选项二"]
            elif question_type == "text":
                result["options"] = []
            else:
                result["question_type"] = "text"
                result["options"] = []

            question = (result.get("question") or "").strip()
            question = question.replace("\n", "").replace("\r", "")
            result["question"] = question
            result["question_length_hint"] = self._calc_question_length_hint(question)

        else:
            result["question_length_hint"] = ""

        return result

    def _build_checkpoint_ask(self, question: str, round_num: int) -> Dict[str, Any]:
        """
        把“该进入阶段整理”的结果，转成“继续提问 + 可整理按钮”的结构。
        """
        safe_question = (question or "").strip()
        if not safe_question:
            safe_question = "如果继续往里走，你最想再补充哪一层自己还没说透的东西？"

        safe_question = safe_question.replace("\n", "").replace("\r", "")
        safe_question = self._trim_question_if_needed(safe_question)

        return {
            "status": "ask",
            "question_type": "text",
            "question": safe_question,
            "options": [],
            "summary": "",
            "report": "",
            "next_action": "",
            "question_length_hint": self._calc_question_length_hint(safe_question),
            "should_end": False,
            "can_summarize": round_num >= self.min_summary_round,
        }

    def _apply_guardrails(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用轻度流程护栏。

        新规则：
        1. 正常 continue 流程里，不再直接把结果切成 stage_summary / final_report
        2. 模型如果觉得“现在适合整理”，转成：
           ask + can_summarize = true
        3. 真正进入阶段整理，只在 stage = summarize 时允许
        """
        round_num = self._safe_round(context)
        status = result.get("status", "")
        stage = str(context.get("stage", "") or "").strip().lower()

        is_manual_summary_stage = stage in ("summarize", "summary", "draft_report", "manual_summary")

        # 手动总结阶段：允许 summary / report 类状态正常通过
        if is_manual_summary_stage:
            result["can_summarize"] = False
            return result

        # 早期阶段：不允许太早出现“可整理”
        if round_num < self.min_summary_round:
            if status in ("stage_summary", "final_report", "action_plan", "draft_report"):
                return self._build_checkpoint_ask(
                    "请继续沿着刚才最有感觉、最有分量的那部分往下说。",
                    round_num=round_num,
                )

            if status in ("ask", "clarify"):
                result["can_summarize"] = False
            return result

        # 正常问答阶段：
        # 如果模型直接给了阶段整理结果，不再强跳，转成 ask + can_summarize=true
        if status in ("stage_summary", "final_report", "action_plan", "draft_report"):
            fallback_question = result.get("question", "") or "如果继续往里走，你最想再补充哪一层自己还没说透的东西？"
            return self._build_checkpoint_ask(
                question=fallback_question,
                round_num=round_num,
            )

        # 轮数较深：即使模型继续 ask，也可以允许出现“先整理一下”按钮
        if status in ("ask", "clarify"):
            if round_num >= self.force_summary_round:
                result["can_summarize"] = True
            else:
                result["can_summarize"] = bool(result.get("can_summarize", False))

        return result

    def _basic_validate_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        对最终结果做基础校验。
        """
        status = result.get("status", "")

        if status in ("ask", "clarify") and not result.get("question"):
            result["status"] = "error"
            result["summary"] = "模型返回了提问状态，但 question 为空。"

        if status == "final_report" and not result.get("report"):
            result["status"] = "error"
            result["summary"] = "模型返回了 final_report 状态，但 report 为空。"

        return result

    def _local_repair_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        在不再次请求模型的情况下，做一次轻度本地修复。
        """
        repaired = self._normalize_result(result)
        repaired = self._repair_shape(repaired)

        status = repaired.get("status", "")
        question_type = repaired.get("question_type", "")
        question = (repaired.get("question") or "").strip()

        if status in ("ask", "clarify"):
            if question_type not in ("text", "single_choice"):
                repaired["question_type"] = "text"
                repaired["options"] = []

            if repaired["question_type"] == "text":
                repaired["options"] = []

            if repaired["question_type"] == "single_choice" and len(repaired.get("options", [])) < 2:
                repaired["options"] = ["选项一", "选项二"]

            question = question.replace("\n", "").replace("\r", "")
            if question.count("？") + question.count("?") > 1:
                first_q_cn = question.find("？")
                first_q_en = question.find("?")
                positions = [p for p in (first_q_cn, first_q_en) if p != -1]
                if positions:
                    first_q = min(positions)
                    question = question[:first_q + 1]

            question = self._trim_question_if_needed(question)
            repaired["question"] = question
            repaired["question_length_hint"] = self._calc_question_length_hint(question)

        return repaired

    def _rewrite_invalid_result(
        self,
        adapter: PromptAdapter,
        invalid_result: Dict[str, Any],
        error_message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        当结果仍不合格时，调用模型进行一次压缩/重写。
        只重写结构，不重写业务方向。
        """
        status = invalid_result.get("status", "")
        question = (invalid_result.get("question") or "").strip()

        if status not in ("ask", "clarify") or not question:
            return invalid_result

        rewrite_prompt = f"""
你将收到一个已经生成但不符合输出约束的问题结果。
你的任务不是改变业务方向，而是在尽量保留原意的前提下，把它改写成一个前端更易展示、更短、更稳的合法 JSON。

当前上下文：
- mode: {context.get("mode", "")}
- round: {context.get("round", 1)}
- answer: {context.get("answer", "")}
- qa_history: {context.get("qa_history", [])}

原始不合格结果：
{json.dumps(invalid_result, ensure_ascii=False)}

当前错误原因：
{error_message}

改写要求：
1. 保持 status 不变，仍然输出 "{status}"
2. 保持问题意图尽量不变
3. question 必须是单句、不得换行
4. question 优先控制在 18~28 个中文字符之间，极限不超过 36 个
5. 不得复合提问
6. 如果 question_type = "single_choice"，必须保留 single_choice，并提供至少两个简短选项
7. 如果 question_type = "text"，options 必须是 []
8. 只输出一个合法 JSON 对象
9. question_length_hint 必须正确填写：short / medium / long
10. can_summarize 必须是 true 或 false

请直接输出最终 JSON。
""".strip()

        messages = self.get_messages(rewrite_prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content
            rewritten = self._parse_json(raw_content)
            rewritten = self._normalize_result(rewritten)
            rewritten = self._repair_shape(rewritten)

            is_valid, validated_data, _ = adapter.basic_validate_response(
                json.dumps(rewritten, ensure_ascii=False)
            )
            if is_valid:
                return self._normalize_result(validated_data)

            return self._local_repair_result(invalid_result)
        except Exception:
            return self._local_repair_result(invalid_result)

    def _finalize_result(self, result: Dict[str, Any], context: Dict[str, Any], adapter: PromptAdapter) -> Dict[str, Any]:
        """
        统一整理最终结果：
        normalize -> repair -> guardrails -> validate -> 必要时 rewrite
        """
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._apply_guardrails(result, context)
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._basic_validate_response(result)

        is_valid, validated_data, error_message = adapter.basic_validate_response(
            json.dumps(result, ensure_ascii=False)
        )
        if is_valid:
            return self._normalize_result(validated_data)

        locally_repaired = self._local_repair_result(result)
        is_valid, validated_data, error_message = adapter.basic_validate_response(
            json.dumps(locally_repaired, ensure_ascii=False)
        )
        if is_valid:
            return self._normalize_result(validated_data)

        rewritten = self._rewrite_invalid_result(
            adapter=adapter,
            invalid_result=locally_repaired,
            error_message=error_message,
            context=context,
        )
        rewritten = self._normalize_result(rewritten)
        rewritten = self._repair_shape(rewritten)
        rewritten = self._basic_validate_response(rewritten)

        is_valid, validated_data, error_message = adapter.basic_validate_response(
            json.dumps(rewritten, ensure_ascii=False)
        )
        if is_valid:
            return self._normalize_result(validated_data)

        return {
            "status": "error",
            "question_type": "",
            "question": "",
            "options": [],
            "summary": f"模型输出未通过校验：{error_message}",
            "report": "",
            "next_action": "",
            "question_length_hint": "",
            "should_end": False,
            "can_summarize": False,
        }

    def run(self, prompt_key: str, **kwargs) -> Dict[str, Any]:
        """
        同步执行某个 prompt。
        """
        if prompt_key not in PROMPT_REGISTRY:
            return {
                "status": "error",
                "question_type": "",
                "question": "",
                "options": [],
                "summary": f"未找到 prompt_key: {prompt_key}",
                "report": "",
                "next_action": "",
                "question_length_hint": "",
                "should_end": False,
                "can_summarize": False,
            }

        config = PROMPT_REGISTRY[prompt_key]
        raw_prompt = config["raw_prompt"]
        scene = config.get("scene", "universal")
        temperature = config.get("temperature", 1.2)

        adapter = PromptAdapter(scene=scene)
        rendered_prompt = adapter.compile(
            raw_prompt=raw_prompt,
            context=kwargs
        )

        messages = self.get_messages(rendered_prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )

        raw_content = response.choices[0].message.content
        result = self._parse_json(raw_content)
        result = self._finalize_result(result=result, context=kwargs, adapter=adapter)
        return result

    def stream(self, prompt_key: str, **kwargs):
        """
        流式执行某个 prompt。

        事件设计：
        - chunk: 大模型原始流式文本片段
        - done: 解析并护栏处理后的最终结构化结果
        - error: 异常信息
        """
        if prompt_key not in PROMPT_REGISTRY:
            yield {
                "event": "error",
                "message": f"未找到 prompt_key: {prompt_key}"
            }
            return

        config = PROMPT_REGISTRY[prompt_key]
        raw_prompt = config["raw_prompt"]
        scene = config.get("scene", "universal")
        temperature = config.get("temperature", 1.2)

        adapter = PromptAdapter(scene=scene)
        rendered_prompt = adapter.compile(
            raw_prompt=raw_prompt,
            context=kwargs
        )

        messages = self.get_messages(rendered_prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )

        buffer = ""

        for chunk in response:
            try:
                delta = chunk.choices[0].delta.content or ""
            except Exception:
                delta = ""

            if delta:
                buffer += delta
                yield {
                    "event": "chunk",
                    "content": delta
                }

        result = self._parse_json(buffer)
        result = self._finalize_result(result=result, context=kwargs, adapter=adapter)

        yield {
            "event": "done",
            "data": result
        }
