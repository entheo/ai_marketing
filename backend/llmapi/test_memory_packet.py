from llmapi.self_value_bot import SelfValueBot


def _build_stage_state():
    return {
        "stage_definition": {
            "stage_id": "discovery",
            "stage_name": "价值挖掘",
        },
        "stage_runtime": {
            "current_maturity": "L2",
            "can_transition": True,
            "stage_snapshot": {
                "stage_summary": "用户价值逐渐清晰",
                "findings": [
                    {"content": "用户擅长结构化表达"},
                    {"content": "用户在咨询场景反馈较好"},
                ],
                "judgements": [
                    {"content": "更适合咨询型服务", "status": "confirmed"},
                    {"content": "暂不适合重运营赛道", "status": "questioned"},
                ],
            },
        },
    }


def _build_qa_history(n=9):
    return [
        {
            "round": i,
            "question": f"问题{i}",
            "answer": f"回答{i}",
        }
        for i in range(1, n + 1)
    ]


def test_runner_context_uses_recent_window():
    bot = SelfValueBot(client=None, model=None)
    context = {
        "round": 9,
        "qa_history": _build_qa_history(9),
        "qa_history_summary": "历史摘要内容",
        "stage_state": _build_stage_state(),
    }
    runner_context = bot._build_runner_context(context)

    assert len(runner_context["qa_history"]) == bot.recent_window_rounds
    assert runner_context["qa_history"][0]["round"] == 4
    assert runner_context["qa_history"][-1]["round"] == 9


def test_runner_context_includes_identity_stage_and_long_term_memory():
    bot = SelfValueBot(client=None, model=None)
    context = {
        "round": 10,
        "qa_history": _build_qa_history(10),
        "qa_history_summary": "这是一个历史摘要",
        "stage_state": _build_stage_state(),
    }
    runner_context = bot._build_runner_context(context)

    assert "咨询教练" in runner_context["identity_kernel"]
    assert runner_context["stage_memory"]["current_stage_id"] == "discovery"
    assert runner_context["long_term_memory"]["confirmed"]
    assert runner_context["long_term_memory"]["rejected_or_questioned"]
    assert runner_context["long_term_memory"]["history_summary"]


def test_long_term_history_summary_is_stable_across_rounds():
    bot = SelfValueBot(client=None, model=None)
    odd_context = {
        "round": 9,
        "qa_history": _build_qa_history(9),
        "qa_history_summary": "仅偶数轮写入历史摘要",
        "stage_state": _build_stage_state(),
    }
    even_context = {
        "round": 10,
        "qa_history": _build_qa_history(10),
        "qa_history_summary": "仅偶数轮写入历史摘要",
        "stage_state": _build_stage_state(),
    }

    odd_memory = bot._build_runner_context(odd_context)["long_term_memory"]["history_summary"]
    even_memory = bot._build_runner_context(even_context)["long_term_memory"]["history_summary"]

    assert odd_memory != ""
    assert even_memory != ""
