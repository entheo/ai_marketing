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
"""

from typing import Any, Dict


class PromptAdapter:
    """
    统一提示词适配器

    核心思想：
    - raw prompt 保持原始业务意图
    - adapter 只增加统一输入输出协议
    - 内容状态由模型根据上下文自行识别
    """

    # 统一的上下文说明协议
    COMMON_STATE_PROTOCOL = """
【上下文说明】
下面是当前交互上下文。你必须结合这些信息判断现在最适合输出什么内容。

- mode: {mode}
- round: {round}
- answer: {answer}
- qa_history: {qa_history}
""".strip()

    # 统一的输出协议
    COMMON_OUTPUT_CONTRACT = """
【输出协议】
你必须只输出一个合法 JSON 对象，不要输出任何额外说明，不要使用 Markdown 代码块，不要输出解释文字。

你需要根据当前上下文，自行识别当前最合适的 status。
status 不是由外部提前规定的，而是由你根据内容判断。

你可输出的 status 包括但不限于：
- ask
- stage_summary
- final_report
- action_plan
- clarify
- error

推荐字段规范如下：

1）如果当前最适合继续提问：
{
  "status": "ask",
  "question_type": "single_choice 或 open",
  "question": "问题内容",
  "options": ["选项1", "选项2"],
  "summary": "",
  "report": "",
  "next_action": "",
  "should_end": false
}

2）如果当前最适合给出阶段性总结：
{
  "status": "stage_summary",
  "question_type": "",
  "question": "",
  "options": [],
  "summary": "阶段性总结内容",
  "report": "",
  "next_action": "建议下一步继续追问或聚焦的方向",
  "should_end": false
}

3）如果当前已经适合输出完整阶段报告：
{
  "status": "final_report",
  "question_type": "",
  "question": "",
  "options": [],
  "summary": "核心结论摘要",
  "report": "完整阶段性报告",
  "next_action": "建议下一步行动",
  "should_end": true
}

4）如果当前信息不足，需要澄清：
{
  "status": "clarify",
  "question_type": "open",
  "question": "澄清问题",
  "options": [],
  "summary": "",
  "report": "",
  "next_action": "",
  "should_end": false
}

5）如果出现异常情况：
{
  "status": "error",
  "question_type": "",
  "question": "",
  "options": [],
  "summary": "错误原因",
  "report": "",
  "next_action": "",
  "should_end": false
}

额外要求：
1. 单选题优先，但不是强制
2. 如果 question_type = "single_choice"，必须提供 options，且至少 2 个
3. 如果 question_type = "open"，options 必须是 []
4. 不要输出 null，尽量输出空字符串或空数组
5. 任何情况下都只能输出合法 JSON
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
        - round
        - answer
        - qa_history
        """
        normalized = dict(context or {})
        normalized.setdefault("mode", "default")
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
            round=self._format_value(context.get("round")),
            answer=self._format_value(context.get("answer")),
            qa_history=self._format_value(context.get("qa_history")),
        )

    def compile(self, raw_prompt: str, context: Dict[str, Any]) -> str:
        """
        编译最终给模型的完整 prompt。

        拼接顺序：
        1. 原始提示词
        2. 当前上下文
        3. 输出协议

        返回：
        - 可直接发给大模型的完整字符串
        """
        input_block = self._build_input_block(context)

        final_prompt = f"""
{raw_prompt}

{input_block}

{self.COMMON_OUTPUT_CONTRACT}
""".strip()

        return final_prompt
