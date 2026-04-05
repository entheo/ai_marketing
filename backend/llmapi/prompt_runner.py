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

    SUMMARY_LIKE_STATUS = ("stage_summary", "final_report", "action_plan", "draft_report")

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
        if length <= 28:
            return "short"
        if length <= 70:
            return "medium"
        return "long"

    def _trim_question_if_needed(self, question: str) -> str:
        """
        极端兜底：
        如果问题异常长，先做非常轻度的本地裁剪。
        """
        question = (question or "").strip().replace("\n", "").replace("\r", "")
        if len(question) <= 140:
            return question

        window = question[:140]
        cut_pos = max(
            window.rfind("。"),
            window.rfind("！"),
            window.rfind("？"),
            window.rfind("."),
            window.rfind("!"),
            window.rfind("?"),
        )
        if cut_pos >= 40:
            trimmed = window[:cut_pos + 1].rstrip("，。、；：,.;: ")
        else:
            trimmed = window.rstrip("，。、；：,.;: ")
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

    def _is_manual_summary_stage(self, context: Dict[str, Any]) -> bool:
        stage = str(context.get("stage", "") or "").strip().lower()
        return stage in ("summarize", "summary", "draft_report", "manual_summary")

    def _looks_like_stuck_answer(self, text: str) -> bool:
        """
        判断用户当前回答是否明显卡住。
        """
        value = str(text or "").strip().lower()
        if not value:
            return False

        stuck_phrases = [
            "不知道",
            "不清楚",
            "说不上来",
            "想不到",
            "没想法",
            "没有了",
            "没了",
            "不确定",
            "卡住了",
            "答不上来",
            "没什么",
            "随便",
            "不太知道",
            "不好说",
            "不知道了",
        ]

        # 超短回答且属于常见卡住表达
        if value in stuck_phrases:
            return True

        if any(phrase in value for phrase in stuck_phrases):
            return True

        return False

    def _is_user_stuck(self, context: Dict[str, Any]) -> bool:
        """
        判断当前用户是否处在明显受阻状态。
        规则：
        1. 当前 answer 明显卡住
        2. 或 qa_history 最后一条回答明显卡住
        """
        current_answer = str(context.get("answer", "") or "").strip()
        if self._looks_like_stuck_answer(current_answer):
            return True

        qa_history = context.get("qa_history", []) or []
        if isinstance(qa_history, list) and qa_history:
            last_item = qa_history[-1] or {}
            last_answer = str(last_item.get("answer", "") or "").strip()
            if self._looks_like_stuck_answer(last_answer):
                return True

        return False

    def _build_checkpoint_ask(self, question: str, round_num: int) -> Dict[str, Any]:
        """
        最后兜底用：
        当模型无法给出合适追问时，保留一个温和的继续入口。
        注意：这不再是主路径。
        """
        safe_question = (question or "").strip()
        if not safe_question:
            if round_num >= self.min_summary_round:
                safe_question = "要不要换个更具体的角度说一小段？"
            else:
                safe_question = "刚才哪一处最接近你真实的感觉？"

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

    def _rewrite_summary_to_followup_question(
        self,
        adapter: PromptAdapter,
        summary_like_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        当模型想总结、但当前阶段还不准备直接总结时，
        不再用固定模板硬拦，而是要求模型换一个角度继续问。
        """
        if self.client is None or self.model is None:
            return {}

        round_num = self._safe_round(context)
        is_stuck = self._is_user_stuck(context)

        stuck_instruction = (
            "用户刚刚明显卡住了。不要重复深挖“还没说透的部分”。"
            "请换一个更具体、更低门槛、更生活化的角度继续问。"
            "优先场景、例子、最近一次经历，必要时可改成 single_choice。"
            if is_stuck
            else
            "不要直接总结。请保留当前探索方向，但换一个角度继续问。"
            "新问题不能与上一问同构，不能只是改写原话。"
        )

        rewrite_prompt = f"""
你将收到一个本来适合做阶段整理的结果。
但当前产品策略是：现在先不直接总结，而是继续问一个新的问题。

你的任务：
把“想总结”的倾向，改写成一个新的 follow-up question，
用于继续引导用户，但不能僵硬、不能重复、不能使用固定模板。

当前上下文：
- mode: {context.get("mode", "")}
- stage: {context.get("stage", "")}
- round: {context.get("round", 1)}
- answer: {context.get("answer", "")}
- qa_history: {context.get("qa_history", [])}

模型原本的结果：
{json.dumps(summary_like_result, ensure_ascii=False)}

改写要求：
1. 只输出一个合法 JSON 对象
2. status 只能是 ask 或 clarify
3. question_type 只能是 text 或 single_choice
4. 如果输出 single_choice，必须提供至少 2 个选项
5. 问题不得换行、不得复合提问
6. 问题优先控制在 28~88 个中文字符，极限不超过 140 个
7. 不允许重复以下类型的抽象追问：
   - 你还有什么没说透
   - 如果继续往里走
   - 你最想再补充什么
8. 问题可以用 1~2 句表达，但只能围绕一个问题焦点
9. 在不生硬的前提下，尽量承接用户上一轮中的关键词或情绪线索
10. {stuck_instruction}
11. 如果当前更适合停一下，也不要直接总结；而是问一个低压力、容易回答的小问题
12. can_summarize:
   - 如果 round >= {self.min_summary_round}，可设为 true
   - 否则必须为 false
13. 不要输出 null，不要输出 markdown 代码块

请直接输出最终 JSON。
""".strip()

        messages = self.get_messages(rewrite_prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
            )
            raw_content = response.choices[0].message.content
            rewritten = self._parse_json(raw_content)
            rewritten = self._normalize_result(rewritten)
            rewritten = self._repair_shape(rewritten)

            is_valid, validated_data, _ = adapter.basic_validate_response(
                json.dumps(rewritten, ensure_ascii=False)
            )
            if is_valid and validated_data.get("status") in ("ask", "clarify"):
                return self._normalize_result(validated_data)

            return {}
        except Exception:
            return {}

    def _apply_guardrails(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用轻度流程护栏。

        新原则：
        1. summarize 阶段允许 summary / report 正常通过
        2. 正常 continue 阶段里，不再把“想总结”直接强改成固定追问
        3. can_summarize 主要用于控制按钮，而不是替代模型发问
        """
        round_num = self._safe_round(context)
        status = result.get("status", "")

        if self._is_manual_summary_stage(context):
            result["can_summarize"] = False
            return result

        # 太早：不允许出现整理按钮
        if round_num < self.min_summary_round:
            if status in ("ask", "clarify"):
                result["can_summarize"] = False
            return result

        # 进入中后段：
        # ask / clarify 可以自然带 summarize 按钮
        if status in ("ask", "clarify"):
            if round_num >= self.force_summary_round:
                result["can_summarize"] = True
            else:
                result["can_summarize"] = bool(result.get("can_summarize", False))
            return result

        # summary-like 状态在这里先不硬改，交给后续专门逻辑处理
        if status in self.SUMMARY_LIKE_STATUS:
            result["can_summarize"] = False
            return result

        return result

    def _convert_summary_like_result_if_needed(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any],
        adapter: PromptAdapter,
    ) -> Dict[str, Any]:
        """
        第一轮自然对话实验：
        临时关闭 summary-like -> ask/clarify 的自动改写链路。
        让模型原始 summary-like 输出直接透传。
        """
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
你的任务不是改变业务方向，而是在尽量保留原意的前提下，把它改写成一个前端可展示、语气自然、信息更有密度的合法 JSON。

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
3. question 不得换行
4. question 优先控制在 28~88 个中文字符之间，极限不超过 140 个
5. 问题可为 1~2 句，但只能围绕一个问题焦点
6. 在不生硬的前提下，尽量承接用户上一轮中的关键词或情绪线索
7. 如果 question_type = "single_choice"，必须保留 single_choice，并提供至少两个简短选项
8. 如果 question_type = "text"，options 必须是 []
9. 只输出一个合法 JSON 对象
10. question_length_hint 必须正确填写：short / medium / long
11. can_summarize 必须是 true 或 false

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
        normalize -> repair -> guardrails -> summary-like conversion -> validate -> 必要时 rewrite
        """
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._apply_guardrails(result, context)

        result = self._convert_summary_like_result_if_needed(
            result=result,
            context=context,
            adapter=adapter,
        )

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
