"""
prompt_adapter.py
=================

工作目的：
把原始提示词（raw prompt）自动整理成统一格式，
让模型输出前端可直接识别的结构化 JSON。

这个模块不负责：
1. 具体业务逻辑判断
2. 决定当前一定是 ask / report / plan
3. 写死业务流程

这个模块只负责：
1. 给 raw prompt 补统一输入说明
2. 给 raw prompt 补统一输出协议
3. 要求模型在输出时自行标注当前识别到的状态
4. 给缺失上下文字段补默认值，减少调用时出错风险
5. 对模型输出做基础结构校验
"""

from typing import Any, Dict, Tuple
import json


class PromptAdapter:
    """
    统一提示词适配器

    核心思想：
    - raw prompt 保持原始业务意图
    - adapter 只增加统一输入输出协议
    - 内容状态由模型根据上下文自行识别
    """

    ALLOWED_STATUS = {
        "ask",
        "stage_summary",
        "final_report",
        "action_plan",
        "clarify",
        "error",
    }

    ALLOWED_QUESTION_TYPES = {
        "",
        "text",
        "single_choice",
    }

    QUESTION_LENGTH_RULE = {
        "ideal_min": 18,
        "ideal_max": 28,
        "hard_max": 36,
    }

    # 统一的上下文说明协议
    COMMON_STATE_PROTOCOL = """
【上下文说明】
下面是当前交互上下文。你必须结合这些信息判断现在最适合输出什么内容。

- mode: {mode}
- stage: {stage}
- round: {round}
- answer: {answer}
- qa_history: {qa_history}
""".strip()

    # 输出结构参考
    SCHEMAS = """
【字段结构参考】

一、继续提问 ask
{
  "status": "ask",
  "question_type": "single_choice 或 text",
  "question": "问题内容",
  "options": ["选项1", "选项2"],
  "summary": "",
  "report": "",
  "next_action": "",
  "question_length_hint": "short / medium / long",
  "should_end": false,
  "can_summarize": false
}

二、阶段性总结 stage_summary
{
  "status": "stage_summary",
  "question_type": "",
  "question": "",
  "options": [],
  "summary": "阶段性总结内容",
  "report": "",
  "next_action": "建议下一步继续追问或聚焦的方向",
  "question_length_hint": "",
  "should_end": false,
  "can_summarize": false
}

三、完整阶段报告 final_report
{
  "status": "final_report",
  "question_type": "",
  "question": "",
  "options": [],
  "summary": "核心结论摘要",
  "report": "完整阶段性报告",
  "next_action": "建议下一步行动",
  "question_length_hint": "",
  "should_end": true,
  "can_summarize": false
}

四、澄清 clarify
{
  "status": "clarify",
  "question_type": "text",
  "question": "澄清问题",
  "options": [],
  "summary": "",
  "report": "",
  "next_action": "",
  "question_length_hint": "short / medium / long",
  "should_end": false,
  "can_summarize": false
}

五、异常 error
{
  "status": "error",
  "question_type": "",
  "question": "",
  "options": [],
  "summary": "错误原因",
  "report": "",
  "next_action": "",
  "question_length_hint": "",
  "should_end": false,
  "can_summarize": false
}
""".strip()

    # 统一的输出协议
    COMMON_OUTPUT_CONTRACT = f"""
【输出协议】
你必须只输出一个合法 JSON 对象，不要输出任何额外说明，不要使用 Markdown 代码块，不要输出解释文字。

【阶段识别原则】
你需要结合 stage 来理解当前任务：

1. 当 stage = "start"
- 目标是开启问答
- 优先输出 ask
- 不要输出 stage_summary / final_report

2. 当 stage = "continue"
- 目标是继续追问或澄清
- 你可以根据内容输出：
  - ask
  - clarify
  - stage_summary
  - final_report
  - action_plan
  - error
- 但如果信息仍不够，请优先 ask / clarify

3. 当 stage = "summarize"
- 目标是基于已有 qa_history 生成阶段性整理
- 此时不允许输出 ask
- 此时不允许输出 clarify
- 必须输出以下之一：
  - stage_summary
  - final_report
- question 必须为空字符串
- question_type 必须为空字符串
- options 必须为 []
- summary 与 report 至少一个非空
- can_summarize 必须为 false

也就是说：
如果 stage = "summarize"，继续提问属于错误输出。

【状态选择原则】
当 stage 不是 summarize 时，你可以根据上下文自行识别当前最合适的 status。
你可输出的 status 包括但不限于：
- ask
- stage_summary
- final_report
- action_plan
- clarify
- error

{SCHEMAS}

【提问长度与展示约束】
如果当前输出的是 ask 或 clarify，问题必须满足以下要求：
1. 每次只问一个问题，不得复合提问
2. 问题必须为单句
3. 不得换行
4. 中文问题优先控制在 {QUESTION_LENGTH_RULE["ideal_min"]} 到 {QUESTION_LENGTH_RULE["ideal_max"]} 个字之间
5. 极限不得超过 {QUESTION_LENGTH_RULE["hard_max"]} 个字
6. 不得添加解释性尾巴，例如：
   - 为什么
   - 或者你也可以
   - 如果你愿意的话
   - 你是否同时
   - 会不会也
7. 问题必须自然、口语化、易回答，不要像分析报告标题
8. 单选题题干要更短、更直接，优先短于开放题

【选项约束】
如果 question_type = "single_choice"：
1. 必须提供 options
2. options 至少 2 个
3. options 最好控制在 2 到 4 个
4. 每个选项尽量简短，优先控制在 4 到 12 个字之间
5. 不要让选项语义过度重叠

【字段约束】
1. 如果 question_type = "single_choice"，必须提供 options，且至少 2 个
2. 如果 question_type = "text"，options 必须是 []
3. 不要输出 null，尽量输出空字符串或空数组
4. 任何情况下都只能输出合法 JSON
5. question_length_hint 规则如下：
   - 0~20 字：short
   - 21~30 字：medium
   - 31~{QUESTION_LENGTH_RULE["hard_max"]} 字：long
   - 非提问状态时填空字符串
6. can_summarize 规则如下：
   - ask / clarify 状态时可为 true 或 false
   - stage_summary / final_report / action_plan / error 时必须为 false

【优先级原则】
如果原始提示词中的表达倾向，与本输出协议发生冲突，
必须优先遵守本输出协议。
尤其是：
- 一次只问一个问题
- 问题必须短、单句、可展示
- summarize 阶段绝不能继续提问
- 不要为了“完整”而牺牲前端稳定展示

【最终原则】
你的输出首先要便于前端稳定展示，其次才是文风完整。
宁可更短、更准，也不要更长、更像“大模型”。
""".strip()

    def __init__(self, scene: str = "universal"):
        """
        初始化适配器

        参数：
        - scene: 工程层面的包装方式，不是业务状态分类
        """
        self.scene = scene

    def _format_value(self, value: Any) -> str:
        """
        将上下文中的值格式化为字符串，避免拼接时报错。

        处理原则：
        - None -> ""
        - 其他值 -> str(value)
        """
        if value is None:
            return ""
        return str(value)

    def _normalize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        对上下文字段做默认值补全，避免调用时因字段缺失而报错。

        统一字段：
        - mode
        - stage
        - round
        - answer
        - qa_history
        """
        normalized = dict(context or {})
        normalized.setdefault("mode", "default")
        normalized.setdefault("stage", "continue")
        normalized.setdefault("round", 1)
        normalized.setdefault("answer", "")
        normalized.setdefault("qa_history", [])
        return normalized

    def _build_input_block(self, context: Dict[str, Any]) -> str:
        """
        构建统一上下文输入块。
        """
        context = self._normalize_context(context)

        return self.COMMON_STATE_PROTOCOL.format(
            mode=self._format_value(context.get("mode")),
            stage=self._format_value(context.get("stage")),
            round=self._format_value(context.get("round")),
            answer=self._format_value(context.get("answer")),
            qa_history=self._format_value(context.get("qa_history")),
        )

    def compile(self, raw_prompt: str, context: Dict[str, Any]) -> str:
        """
        编译最终给模型的完整 prompt。
        """
        input_block = self._build_input_block(context)

        final_prompt = f"""
{raw_prompt}

{input_block}

{self.COMMON_OUTPUT_CONTRACT}
""".strip()

        return final_prompt

    def _calc_question_length_hint(self, question: str) -> str:
        """
        根据问题长度计算前端展示提示字段。
        """
        length = len((question or "").strip())
        if length == 0:
            return ""
        if length <= 20:
            return "short"
        if length <= 30:
            return "medium"
        return "long"

    def basic_validate_response(self, response_text: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        对模型输出做基础结构校验。

        返回：
        - is_valid: 是否通过
        - data: 解析后的 JSON；如果失败则为 {{}}
        - error_message: 错误信息；成功则为空字符串
        """
        if not response_text or not str(response_text).strip():
            return False, {{}}, "模型返回为空"

        try:
            data = json.loads(response_text)
        except Exception as e:
            return False, {{}}, f"模型输出不是合法 JSON：{e}"

        if not isinstance(data, dict):
            return False, data, "模型输出必须是 JSON 对象"

        status = str(data.get("status", "")).strip()
        if not status:
            return False, data, "缺少 status"
        if status not in self.ALLOWED_STATUS:
            return False, data, f"不支持的 status：{status}"

        question_type = str(data.get("question_type", "")).strip()
        if question_type not in self.ALLOWED_QUESTION_TYPES:
            return False, data, f"不支持的 question_type：{question_type}"

        data.setdefault("question", "")
        data.setdefault("options", [])
        data.setdefault("summary", "")
        data.setdefault("report", "")
        data.setdefault("next_action", "")
        data.setdefault("question_length_hint", "")
        data.setdefault("should_end", False)
        data.setdefault("can_summarize", False)

        if not isinstance(data["options"], list):
            return False, data, "options 必须是数组"

        data["can_summarize"] = bool(data.get("can_summarize", False))
        data["should_end"] = bool(data.get("should_end", False))

        if status in {"ask", "clarify"}:
            question = str(data.get("question", "")).strip()

            if not question:
                return False, data, f"{status} 状态下 question 不能为空"

            if "\n" in question or "\r" in question:
                return False, data, "question 不能包含换行"

            if len(question) > self.QUESTION_LENGTH_RULE["hard_max"]:
                return False, data, (
                    f'question 超过长度上限：{len(question)} > '
                    f'{self.QUESTION_LENGTH_RULE["hard_max"]}'
                )

            if question.count("？") + question.count("?") > 1:
                return False, data, "question 不能包含多个问号"

            if question_type not in {"text", "single_choice"}:
                return False, data, f"{status} 状态下 question_type 必须是 text 或 single_choice"

            if question_type == "single_choice":
                if len(data["options"]) < 2:
                    return False, data, "single_choice 至少需要 2 个 options"
            elif question_type == "text":
                if data["options"] != []:
                    return False, data, 'text 类型下 options 必须是 []'

            expected_hint = self._calc_question_length_hint(question)
            if not data.get("question_length_hint"):
                data["question_length_hint"] = expected_hint

        else:
            # 非提问状态下 question 相关字段应为空
            if str(data.get("question", "")).strip():
                return False, data, f"{status} 状态下 question 必须为空"

            if str(data.get("question_type", "")).strip():
                return False, data, f"{status} 状态下 question_type 必须为空"

            if data["options"] != []:
                return False, data, f"{status} 状态下 options 必须是 []"

            data["question_length_hint"] = ""

            if status == "stage_summary":
                summary = str(data.get("summary", "")).strip()
                report = str(data.get("report", "")).strip()
                if not summary and not report:
                    return False, data, "stage_summary 状态下 summary 与 report 不能同时为空"

            if status == "final_report":
                report = str(data.get("report", "")).strip()
                if not report:
                    return False, data, "final_report 状态下 report 不能为空"

            if data.get("can_summarize") is not False:
                data["can_summarize"] = False

        return True, data, ""
