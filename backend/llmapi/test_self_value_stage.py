"""
test_self_value_stage.py
========================

工作目的：
测试 self_value_bot + stage_orchestrator + stage_layer 是否已经串通。

测试内容：
1. 第一轮调用 self_value_response，拿到组合结果
2. 第二轮带着 stage_state 继续调用，看是否能恢复并推进
3. 从 confirmation_candidates 中取一个 candidate_id，测试 apply_stage_feedback
4. 测试 try_stage_transition

使用前提：
- llmapi/self_value_bot.py 已替换为接入阶段层的版本
- llmapi/stage_layer.py 已存在
- llmapi/stage_orchestrator.py 已存在
- PromptRunner / PromptAdapter 等仍可正常工作
- 你本地已有可用 client / model，或先用你项目里现成的初始化方式

注意：
- 这里的 client 初始化部分，你需要按自己项目真实情况替换
"""

import json
from llmapi.self_value_bot import SelfValueBot


def print_block(title: str, data):
    print(f"\n{'=' * 18} {title} {'=' * 18}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_bot() -> SelfValueBot:
    """
    你需要按自己的项目实际情况改这里。
    如果你原来已有 client 初始化方式，直接复用。
    """

    # ===== 示例 1：如果你项目里本来就是 client + model 传入 =====
    # from some_module import client
    # return SelfValueBot(client=client, model="gpt-4o-mini")

    # ===== 示例 2：先不接真实模型，只看结构能不能跑通 =====
    # 但注意：如果没有真实 client，runner.run 仍会失败。
    # 所以一般这里还是要接你项目里现有 client。
    raise NotImplementedError("请在 build_bot() 中接入你项目实际可用的 client 和 model")


def main():
    bot = build_bot()

    conversation_id = "conv_stage_demo_001"

    # -------------------------
    # 第一轮：正常调用
    # -------------------------
    result_1 = bot.self_value_response(
        round=1,
        answer="过去几年里，我最擅长的是快速看清一个项目真正卡在哪里。",
        qa_history=[],
        conversation_id=conversation_id,
    )

    print_block("第一轮完整结果", result_1)

    stage_state_1 = result_1.get("stage_state")
    if not stage_state_1:
        raise RuntimeError("第一轮没有返回 stage_state，说明阶段层没有接通")

    # -------------------------
    # 第二轮：带着 stage_state 继续调用
    # -------------------------
    result_2 = bot.self_value_response(
        round=2,
        answer="而且别人经常来找我，不是让我执行，而是让我帮他们判断方向。",
        qa_history=[
            {
                "question": "过去五年，哪件事你做得比大多数人轻松？",
                "answer": "我最擅长快速看清项目真正卡点。"
            }
        ],
        conversation_id=conversation_id,
        stage_state=stage_state_1,
    )

    print_block("第二轮完整结果", result_2)

    stage_state_2 = result_2.get("stage_state")
    if not stage_state_2:
        raise RuntimeError("第二轮没有返回 stage_state")

    # -------------------------
    # 读取 confirmation_candidates
    # -------------------------
    snapshot = (
        stage_state_2.get("stage_runtime", {})
        .get("stage_snapshot", {})
    )
    candidates = snapshot.get("confirmation_candidates", [])

    print_block("当前 confirmation_candidates", candidates)

    # -------------------------
    # 若有待确认项，测试反馈回流
    # -------------------------
    if candidates:
        candidate_id = candidates[0]["id"]

        feedback_result = bot.apply_stage_feedback(
            candidate_id=candidate_id,
            action="confirmed",
            conversation_id=conversation_id,
            stage_state=stage_state_2,
        )

        print_block("用户确认后的结果", feedback_result)

        stage_state_after_feedback = feedback_result.get("stage_state")
        if not stage_state_after_feedback:
            raise RuntimeError("反馈后没有返回 stage_state")

        # -------------------------
        # 尝试切阶段
        # -------------------------
        transition_result = bot.try_stage_transition(
            conversation_id=conversation_id,
            stage_state=stage_state_after_feedback,
        )

        print_block("尝试切阶段后的结果", transition_result)

    else:
        print("\n没有 confirmation_candidates，本轮无法测试反馈与切阶段。")
        print("这不一定是错误，可能只是当前材料还不足以形成确认项。")


if __name__ == "__main__":
    main()
