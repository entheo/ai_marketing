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

        # 轻度护栏配置
        # min_summary_round:
        #   在这个轮数之前，不允许模型过早进入 stage_summary / final_report / action_plan
        self.min_summary_round = 4

        # force_summary_round:
        #   超过这个轮数后，如果模型还一直 ask，程序会将结果改造成 stage_summary，
        #   避免无限发散
        self.force_summary_round = 8

    def get_messages(self, rendered_prompt: str):
        """
        构建 messages。

        这里故意不再单独额外注入 system role，
        因为角色定义已经在 raw prompt 中。
        这样可以避免角色写两遍导致冲突。
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

        有些模型虽然被要求“只输出 JSON”，
        但偶尔还是可能夹带说明文字或代码块。
        这里做一个较保守的提取策略：
        - 优先直接整体解析
        - 如果失败，则尝试截取从第一个 { 到最后一个 } 的内容

        这不是完美方案，但对常见脏返回足够实用。
        """
        text = (raw_text or "").strip()

        # 去掉 markdown 代码块包裹
        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        # 如果本身就是大概率 JSON，直接返回
        if text.startswith("{") and text.endswith("}"):
            return text

        # 尝试抽取最外层 JSON 对象
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]

        return text

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """
        解析模型返回的 JSON。

        返回：
        - 成功：解析后的 dict
        - 失败：统一错误结构
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
                "should_end": False,
                "raw_content": raw_text,
            }

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一补全输出字段，避免前端因为字段缺失而出错。

        统一字段：
        - status
        - question_type
        - question
        - options
        - summary
        - report
        - next_action
        - should_end
        """
        normalized = dict(result or {})

        normalized.setdefault("status", "error")
        normalized.setdefault("question_type", "")
        normalized.setdefault("question", "")
        normalized.setdefault("options", [])
        normalized.setdefault("summary", "")
        normalized.setdefault("report", "")
        normalized.setdefault("next_action", "")
        normalized.setdefault("should_end", False)

        # 强制修正 options 类型
        if not isinstance(normalized.get("options"), list):
            normalized["options"] = []

        # 强制修正 should_end 类型
        normalized["should_end"] = bool(normalized.get("should_end", False))

        return normalized

    def _repair_shape(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据 status 修复结构，确保返回更稳定。

        例如：
        - single_choice 没有 options -> 自动补默认值
        - open 问题带了 options -> 清空 options
        """
        status = result.get("status", "")
        question_type = result.get("question_type", "")
        options = result.get("options", [])

        if status in ("ask", "clarify"):
            if question_type == "single_choice":
                if not isinstance(options, list) or len(options) < 2:
                    result["options"] = ["选项一", "选项二"]
            elif question_type == "open":
                result["options"] = []

        return result

    def _apply_guardrails(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用轻度流程护栏。

        设计原则：
        1. 不提前替模型定义内容状态
        2. 只在明显失控的情况下轻微修正
        3. 护栏要轻，不要过度接管

        当前护栏策略：
        - 前 min_summary_round 轮：不允许过早输出 stage_summary / final_report / action_plan
        - 超过 force_summary_round 轮：如果模型还一直 ask，则转成 stage_summary，避免无限发散
        """
        round_num = self._safe_round(context)
        status = result.get("status", "")

        # 护栏1：前几轮不允许过早总结
        if round_num < self.min_summary_round:
            if status in ("stage_summary", "final_report", "action_plan"):
                return {
                    "status": "ask",
                    "question_type": "open",
                    "question": "请继续沿着刚才最有感觉、最有分量的那部分往下说。",
                    "options": [],
                    "summary": "",
                    "report": "",
                    "next_action": "",
                    "should_end": False,
                }

        # 护栏2：超过一定轮数后，如果还在 ask，强制收一层阶段总结
        if round_num > self.force_summary_round:
            if status == "ask":
                return {
                    "status": "stage_summary",
                    "question_type": "",
                    "question": "",
                    "options": [],
                    "summary": "当前对话已经积累了足够多的线索，适合先做一轮阶段性收束，避免继续发散。",
                    "report": "",
                    "next_action": "请基于已有问答，整理用户当前最明显的价值线索、身份感冲突与下一步值得继续验证的方向。",
                    "should_end": False,
                }

        return result

    def _basic_validate_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        对最终结果做基础校验。

        校验目标不是“绝对正确”，
        而是保证结构上最少可用。

        这里主要检查：
        - ask / clarify 必须有 question
        - final_report 最好有 report
        """
        status = result.get("status", "")

        if status in ("ask", "clarify") and not result.get("question"):
            result["status"] = "error"
            result["summary"] = "模型返回了提问状态，但 question 为空。"

        if status == "final_report" and not result.get("report"):
            result["status"] = "error"
            result["summary"] = "模型返回了 final_report 状态，但 report 为空。"

        return result

    def run(self, prompt_key: str, **kwargs) -> Dict[str, Any]:
        """
        同步执行某个 prompt。

        参数：
        - prompt_key: 注册表中的 prompt 名称
        - kwargs: 当前上下文，如 round / answer / qa_history 等

        返回：
        - 标准化后的 JSON dict
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
                "should_end": False,
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
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._apply_guardrails(result, kwargs)
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._basic_validate_response(result)

        return result

    def stream(self, prompt_key: str, **kwargs):
        """
        流式执行某个 prompt。

        事件设计：
        - chunk: 大模型原始流式文本片段
        - done: 解析并护栏处理后的最终结构化结果
        - error: 异常信息

        注意：
        流式阶段先把原始文本逐段返回给前端，
        最后再统一解析 JSON 并进行轻度护栏处理。
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
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._apply_guardrails(result, kwargs)
        result = self._normalize_result(result)
        result = self._repair_shape(result)
        result = self._basic_validate_response(result)

        yield {
            "event": "done",
            "data": result
        }
