import json
from . import prompt_selfvalue as ps


class SelfValueBot:
    def __init__(self, client=None, model=None):
        self.client = client
        self.model = model
        self.role = """
你是一位擅长通过连续追问帮助用户识别自我价值线索的引导者。
你的目标不是营销，不是商业分析，不是品牌定位。
你只关注用户个人在价值感、身份感、方向感上的真实状态。
"""

    def get_messages(self, rendered_template, use_dict=False):
        messages = [
            {
                "role": "system",
                "content": self.role,
            },
            {
                "role": "user",
                "content": rendered_template
            }
        ]

        if use_dict is True:
            messages.append({
                "role": "assistant",
                "content": "{",
                "partial": True
            })

        return messages

    def self_value_response(self, **kwargs):
        print('SELF VALUE KWARGS:', kwargs)

        round_num = kwargs.get("round", 1)
        min_round = 5
        max_round = 8

        ask_kwargs = dict(kwargs)
        ask_kwargs.setdefault("round", 1)
        ask_kwargs.setdefault("answer", "")

        rendered_template = ps.prompt_ask.format(**ask_kwargs)
        use_dict = False

        messages = self.get_messages(rendered_template, use_dict)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1.5,
        )

        res = response.choices[0].message.content
        print("SELF VALUE 返回内容：", res)

        try:
            res_json = json.loads(res)
        except Exception as e:
            print("ASK JSON解析失败:", e)
            return res

        mode = res_json.get("mode")

        if round_num < min_round:
            if mode == "draft_report":
                return {
                    "mode": "ask",
                    "question": "请继续沿着刚才最有感觉的部分往下说。",
                    "type": "text",
                    "options": [],
                    "should_end": False
                }
            return res_json

        if min_round <= round_num <= max_round:
            if mode == "ask":
                return res_json

            if mode == "draft_report":
                report = self._generate_draft_report(**kwargs)
                return {
                    "mode": "draft_report",
                    "report": report,
                    "should_end": False
                }

            return res_json

        if round_num > max_round:
            report = self._generate_draft_report(**kwargs)
            return {
                "mode": "draft_report",
                "report": report,
                "should_end": False
            }

        return res_json

    def _generate_draft_report(self, **kwargs):
        draft_kwargs = dict(kwargs)
        draft_kwargs.setdefault("answer", "")

        rendered_template = ps.prompt_draft_report.format(**draft_kwargs)
        messages = self.get_messages(rendered_template, use_dict=False)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1.2,
        )

        return response.choices[0].message.content

    def self_value_stream(self, **kwargs):
        """
        流式输出策略：
        - ask：后端流式收集，但前端不逐字展示问题，等收完整个 JSON 后一次性切题
        - draft_report：前端逐段展示 report
        """
        round_num = kwargs.get("round", 1)
        min_round = 5
        max_round = 8

        ask_kwargs = dict(kwargs)
        ask_kwargs.setdefault("round", 1)
        ask_kwargs.setdefault("answer", "")

        rendered_template = ps.prompt_ask.format(**ask_kwargs)
        messages = self.get_messages(rendered_template, use_dict=False)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1.5,
            stream=True,
        )

        ask_buffer = ""

        for chunk in response:
            try:
                delta = chunk.choices[0].delta.content or ""
            except Exception:
                delta = ""

            if delta:
                ask_buffer += delta
                yield {
                    "event": "ask_chunk",
                    "content": delta
                }

        try:
            ask_json = json.loads(ask_buffer)
        except Exception as e:
            yield {
                "event": "error",
                "message": f"ASK JSON解析失败: {str(e)}"
            }
            return

        mode = ask_json.get("mode")

        if round_num < min_round:
            if mode == "draft_report":
                ask_json = {
                    "mode": "ask",
                    "question": "请继续沿着刚才最有感觉的部分往下说。",
                    "type": "text",
                    "options": [],
                    "should_end": False
                }

            yield {
                "event": "ask_done",
                "data": ask_json
            }
            return

        if min_round <= round_num <= max_round:
            if mode == "ask":
                yield {
                    "event": "ask_done",
                    "data": ask_json
                }
                return

            if mode == "draft_report":
                for item in self._stream_draft_report(**kwargs):
                    yield item
                return

            yield {
                "event": "ask_done",
                "data": ask_json
            }
            return

        if round_num > max_round:
            for item in self._stream_draft_report(**kwargs):
                yield item
            return

    def _stream_draft_report(self, **kwargs):
        draft_kwargs = dict(kwargs)
        draft_kwargs.setdefault("answer", "")

        rendered_template = ps.prompt_draft_report.format(**draft_kwargs)
        messages = self.get_messages(rendered_template, use_dict=False)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1.2,
            stream=True,
        )

        full_report = ""

        yield {
            "event": "draft_report_start"
        }

        for chunk in response:
            try:
                delta = chunk.choices[0].delta.content or ""
            except Exception:
                delta = ""

            if delta:
                full_report += delta
                yield {
                    "event": "draft_report_delta",
                    "content": delta
                }

        yield {
            "event": "draft_report_done",
            "data": {
                "mode": "draft_report",
                "report": full_report,
                "should_end": False
            }
        }
