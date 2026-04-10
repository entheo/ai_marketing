from llmapi.prompt_runner import PromptRunner


def test_get_messages_adds_system_rule_card():
    runner = PromptRunner(client=None, model=None)

    messages = runner.get_messages("hello")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "提问交互规则" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"].startswith("hello")


def test_get_messages_adds_late_round_reminder():
    runner = PromptRunner(client=None, model=None)

    early = runner.get_messages("prompt", context={"round": 8})
    late = runner.get_messages("prompt", context={"round": 22})

    assert "晚轮规则重申" not in early[1]["content"]
    assert "晚轮规则重申" in late[1]["content"]
