"""
stage_layer.py
==============

工作目的：
为多阶段方法论提供统一的“阶段定义层 + 阶段运行层”。

它负责：
1. 定义方法论阶段的静态结构（阶段是什么）
2. 保存阶段运行状态（阶段走到哪）
3. 承载阶段成果快照（右侧成果区的基础数据）
4. 根据阶段产出推断成熟度
5. 处理右侧确认反馈并回流到阶段状态
6. 判断阶段是否可切换
7. 生成恢复会话所需的最小快照

它不负责：
1. 直接调用大模型
2. 直接拼接 PromptAdapter 输出协议
3. 直接处理前端 UI 展示细节
4. 替代 PromptRunner 的运行时护栏

设计原则：
- 方法论定义层 与 运行状态层分离
- 结果尽量轻、稳、可落盘
- 不依赖具体前端
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy
import uuid


# =========================
# 基础枚举
# =========================

class MaturityLevel(str, Enum):
    """
    阶段成熟度：
    L0: 未成型
    L1: 初步成型
    L2: 可收束
    L3: 可确认
    """
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class StageRunStatus(str, Enum):
    """
    阶段运行状态
    """
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ItemStatus(str, Enum):
    """
    通用成果项状态
    """
    ACTIVE = "active"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    REVISED = "revised"
    QUESTIONED = "questioned"
    NEEDS_REVIEW = "needs_review"
    UNDER_REVISION = "under_revision"
    DISCARDED = "discarded"


class ConfirmationImpact(str, Enum):
    """
    待确认项流程影响级别
    """
    NON_BLOCKING = "non_blocking"
    BLOCKING = "blocking"


class FeedbackAction(str, Enum):
    """
    用户轻交互动作
    """
    CONFIRMED = "confirmed"   # 贴近
    REJECTED = "rejected"     # 不太对
    REVISED = "revised"       # 补一句


# =========================
# 阶段定义层
# =========================

@dataclass
class StageDefinition:
    """
    阶段静态定义
    """
    stage_id: str
    stage_name: str
    stage_goal: str
    coverage_scope: List[str] = field(default_factory=list)
    output_direction: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MethodDefinition:
    """
    方法论静态定义
    """
    method_id: str
    method_name: str
    stages: List[StageDefinition]

    def get_stage(self, stage_id: str) -> Optional[StageDefinition]:
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def get_first_stage(self) -> Optional[StageDefinition]:
        return self.stages[0] if self.stages else None

    def get_next_stage(self, current_stage_id: str) -> Optional[StageDefinition]:
        for i, stage in enumerate(self.stages):
            if stage.stage_id == current_stage_id:
                if i + 1 < len(self.stages):
                    return self.stages[i + 1]
                return None
        return None


# =========================
# 阶段成果对象
# =========================

@dataclass
class Finding:
    id: str
    content: str
    status: str = ItemStatus.ACTIVE.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Judgement:
    id: str
    content: str
    status: str = ItemStatus.ACTIVE.value
    supported_by: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConfirmationCandidate:
    id: str
    source_judgement_id: str
    content: str
    impact: str = ConfirmationImpact.NON_BLOCKING.value
    status: str = "pending"
    user_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StageSnapshot:
    """
    右侧成果区 / 恢复快照核心对象
    """
    method_id: str
    stage_id: str
    stage_name: str
    stage_summary: str = ""
    findings: List[Finding] = field(default_factory=list)
    judgements: List[Judgement] = field(default_factory=list)
    confirmation_candidates: List[ConfirmationCandidate] = field(default_factory=list)
    next_prompt_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method_id": self.method_id,
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "stage_summary": self.stage_summary,
            "findings": [item.to_dict() for item in self.findings],
            "judgements": [item.to_dict() for item in self.judgements],
            "confirmation_candidates": [item.to_dict() for item in self.confirmation_candidates],
            "next_prompt_hint": self.next_prompt_hint,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StageSnapshot":
        return cls(
            method_id=data.get("method_id", ""),
            stage_id=data.get("stage_id", ""),
            stage_name=data.get("stage_name", ""),
            stage_summary=data.get("stage_summary", ""),
            findings=[Finding(**item) for item in (data.get("findings") or [])],
            judgements=[Judgement(**item) for item in (data.get("judgements") or [])],
            confirmation_candidates=[
                ConfirmationCandidate(**item)
                for item in (data.get("confirmation_candidates") or [])
            ],
            next_prompt_hint=data.get("next_prompt_hint", ""),
        )


# =========================
# 阶段运行层
# =========================

@dataclass
class StageRuntime:
    """
    当前阶段运行状态
    """
    current_maturity: str = MaturityLevel.L0.value
    stage_snapshot: Optional[StageSnapshot] = None
    can_transition: bool = False
    has_blocking_confirmation: bool = False
    last_feedback_event: Optional[Dict[str, Any]] = None
    next_prompt_hint: str = ""
    status: str = StageRunStatus.ACTIVE.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_maturity": self.current_maturity,
            "stage_snapshot": self.stage_snapshot.to_dict() if self.stage_snapshot else None,
            "can_transition": self.can_transition,
            "has_blocking_confirmation": self.has_blocking_confirmation,
            "last_feedback_event": deepcopy(self.last_feedback_event),
            "next_prompt_hint": self.next_prompt_hint,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StageRuntime":
        snapshot_data = data.get("stage_snapshot")
        return cls(
            current_maturity=data.get("current_maturity", MaturityLevel.L0.value),
            stage_snapshot=StageSnapshot.from_dict(snapshot_data) if snapshot_data else None,
            can_transition=bool(data.get("can_transition", False)),
            has_blocking_confirmation=bool(data.get("has_blocking_confirmation", False)),
            last_feedback_event=deepcopy(data.get("last_feedback_event")),
            next_prompt_hint=data.get("next_prompt_hint", ""),
            status=data.get("status", StageRunStatus.ACTIVE.value),
        )


@dataclass
class StageState:
    """
    系统消费的最小阶段对象：
    阶段定义层 + 阶段运行层
    """
    stage_definition: StageDefinition
    stage_runtime: StageRuntime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_definition": self.stage_definition.to_dict(),
            "stage_runtime": self.stage_runtime.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StageState":
        return cls(
            stage_definition=StageDefinition(**data["stage_definition"]),
            stage_runtime=StageRuntime.from_dict(data["stage_runtime"]),
        )


@dataclass
class ConversationResumeSnapshot:
    """
    恢复会话的最小快照
    """
    conversation_id: str
    method_id: str
    current_stage_id: str
    current_stage_maturity: str
    stage_snapshot: Optional[StageSnapshot]
    has_blocking_pending_confirmation: bool
    next_prompt_hint: str
    last_feedback_event: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "method_id": self.method_id,
            "current_stage_id": self.current_stage_id,
            "current_stage_maturity": self.current_stage_maturity,
            "stage_snapshot": self.stage_snapshot.to_dict() if self.stage_snapshot else None,
            "has_blocking_pending_confirmation": self.has_blocking_pending_confirmation,
            "next_prompt_hint": self.next_prompt_hint,
            "last_feedback_event": deepcopy(self.last_feedback_event),
        }


# =========================
# 阶段原始产出（供转译层输入）
# =========================

@dataclass
class RawStageOutput:
    """
    方法论层阶段原始产出
    """
    stage_summary: str = ""
    raw_findings: List[str] = field(default_factory=list)
    raw_judgements: List[str] = field(default_factory=list)
    internal_gap_hint: str = ""
    next_prompt_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =========================
# 阶段转译配置
# =========================

@dataclass
class StageTranslateConfig:
    max_findings: int = 3
    max_judgements: int = 2
    max_confirmation_candidates: int = 2


# =========================
# 阶段层核心服务
# =========================

class StageLayer:
    """
    阶段层核心服务
    """

    def __init__(self, method_definition: MethodDefinition):
        self.method_definition = method_definition

    # -------------------------
    # 初始化
    # -------------------------

    def create_initial_stage_state(self) -> StageState:
        first_stage = self.method_definition.get_first_stage()
        if first_stage is None:
            raise ValueError("method_definition.stages 不能为空")

        snapshot = StageSnapshot(
            method_id=self.method_definition.method_id,
            stage_id=first_stage.stage_id,
            stage_name=first_stage.stage_name,
            stage_summary="",
            findings=[],
            judgements=[],
            confirmation_candidates=[],
            next_prompt_hint="开始当前阶段的探索",
        )

        runtime = StageRuntime(
            current_maturity=MaturityLevel.L0.value,
            stage_snapshot=snapshot,
            can_transition=False,
            has_blocking_confirmation=False,
            last_feedback_event=None,
            next_prompt_hint=snapshot.next_prompt_hint,
            status=StageRunStatus.ACTIVE.value,
        )

        return StageState(
            stage_definition=first_stage,
            stage_runtime=runtime,
        )

    # -------------------------
    # 转译层：原始阶段产出 -> StageSnapshot
    # -------------------------

    def translate_raw_stage_output(
        self,
        stage_definition: StageDefinition,
        raw_output: RawStageOutput,
        config: Optional[StageTranslateConfig] = None,
    ) -> StageSnapshot:
        cfg = config or StageTranslateConfig()

        findings = [
            Finding(id=self._new_id("f"), content=self._clean_text(text))
            for text in (raw_output.raw_findings or [])[:cfg.max_findings]
            if self._clean_text(text)
        ]

        judgements = [
            Judgement(
                id=self._new_id("j"),
                content=self._clean_text(text),
                status=ItemStatus.ACTIVE.value,
                supported_by=[item.id for item in findings],
            )
            for text in (raw_output.raw_judgements or [])[:cfg.max_judgements]
            if self._clean_text(text)
        ]

        confirmation_candidates = self._build_confirmation_candidates(
            judgements=judgements,
            max_items=cfg.max_confirmation_candidates,
        )

        snapshot = StageSnapshot(
            method_id=self.method_definition.method_id,
            stage_id=stage_definition.stage_id,
            stage_name=stage_definition.stage_name,
            stage_summary=self._clean_text(raw_output.stage_summary),
            findings=findings,
            judgements=judgements,
            confirmation_candidates=confirmation_candidates,
            next_prompt_hint=self._clean_text(raw_output.next_prompt_hint),
        )
        return snapshot

    def _build_confirmation_candidates(
        self,
        judgements: List[Judgement],
        max_items: int = 2,
    ) -> List[ConfirmationCandidate]:
        """
        第一版保守策略：
        - 默认只从 judgement 里挑前 1~2 条
        - impact 先按轻规则判断
        """
        result: List[ConfirmationCandidate] = []
        for judgement in judgements[:max_items]:
            impact = self._infer_confirmation_impact(judgement.content)
            result.append(
                ConfirmationCandidate(
                    id=self._new_id("c"),
                    source_judgement_id=judgement.id,
                    content=judgement.content,
                    impact=impact,
                    status="pending",
                    user_note="",
                )
            )
        return result

    def _infer_confirmation_impact(self, text: str) -> str:
        """
        第一版极简规则：
        命中“方向 / 角色 / 核心价值 / 适合 / 不适合 / 目标对象”等，
        视为更可能影响后续阶段路径，判为 blocking。
        """
        value = self._clean_text(text)
        if not value:
            return ConfirmationImpact.NON_BLOCKING.value

        blocking_keywords = [
            "核心价值", "价值方向", "更适合", "不适合",
            "角色", "路径", "方向", "目标对象", "主要阻力",
            "当前最强", "最适合", "优先走",
        ]

        if any(word in value for word in blocking_keywords):
            return ConfirmationImpact.BLOCKING.value
        return ConfirmationImpact.NON_BLOCKING.value

    # -------------------------
    # 成熟度推断
    # -------------------------

    def infer_maturity_from_snapshot(self, snapshot: StageSnapshot) -> str:
        findings = snapshot.findings or []
        judgements = snapshot.judgements or []
        confirmation_candidates = snapshot.confirmation_candidates or []

        if not findings and not judgements:
            return MaturityLevel.L0.value

        if findings and not judgements:
            return MaturityLevel.L1.value

        if judgements:
            maturity = MaturityLevel.L2.value
            if self._has_confirmation_worthy_candidate(confirmation_candidates):
                maturity = MaturityLevel.L3.value
            return maturity

        return MaturityLevel.L0.value

    def _has_confirmation_worthy_candidate(
        self,
        candidates: List[ConfirmationCandidate],
    ) -> bool:
        return any(
            candidate.status == "pending"
            for candidate in (candidates or [])
        )

    # -------------------------
    # 运行态更新
    # -------------------------

    def update_stage_state_from_raw_output(
        self,
        stage_state: StageState,
        raw_output: RawStageOutput,
        config: Optional[StageTranslateConfig] = None,
    ) -> StageState:
        """
        用新的阶段原始产出更新阶段状态
        """
        new_state = deepcopy(stage_state)
        snapshot = self.translate_raw_stage_output(
            stage_definition=new_state.stage_definition,
            raw_output=raw_output,
            config=config,
        )

        maturity = self.infer_maturity_from_snapshot(snapshot)
        has_blocking_confirmation = self._detect_blocking_pending(snapshot)

        new_state.stage_runtime.stage_snapshot = snapshot
        new_state.stage_runtime.current_maturity = maturity
        new_state.stage_runtime.has_blocking_confirmation = has_blocking_confirmation
        new_state.stage_runtime.can_transition = self._can_transition(
            maturity=maturity,
            has_blocking_confirmation=has_blocking_confirmation,
        )
        new_state.stage_runtime.next_prompt_hint = (
            snapshot.next_prompt_hint or self._default_next_prompt_hint(maturity)
        )
        new_state.stage_runtime.status = StageRunStatus.ACTIVE.value

        return new_state

    def _detect_blocking_pending(self, snapshot: StageSnapshot) -> bool:
        for item in (snapshot.confirmation_candidates or []):
            if (
                item.impact == ConfirmationImpact.BLOCKING.value
                and item.status == "pending"
            ):
                return True
        return False

    def _can_transition(self, maturity: str, has_blocking_confirmation: bool) -> bool:
        if maturity in (MaturityLevel.L2.value, MaturityLevel.L3.value):
            return not has_blocking_confirmation
        return False

    def _default_next_prompt_hint(self, maturity: str) -> str:
        if maturity == MaturityLevel.L0.value:
            return "继续收集当前阶段的基础材料"
        if maturity == MaturityLevel.L1.value:
            return "继续补足关键发现，尝试形成阶段判断"
        if maturity == MaturityLevel.L2.value:
            return "当前阶段已可收束，可进入下一阶段或补一轮确认"
        if maturity == MaturityLevel.L3.value:
            return "优先处理关键确认项，再决定是否切换阶段"
        return "继续当前阶段"

    # -------------------------
    # 用户反馈回流
    # -------------------------

    def apply_feedback(
        self,
        stage_state: StageState,
        candidate_id: str,
        action: str,
        user_note: str = "",
    ) -> StageState:
        """
        处理右侧反馈：
        - confirmed
        - rejected
        - revised
        """
        new_state = deepcopy(stage_state)
        snapshot = new_state.stage_runtime.stage_snapshot
        if snapshot is None:
            return new_state

        candidate = self._find_candidate(snapshot, candidate_id)
        if candidate is None:
            return new_state

        candidate.user_note = self._clean_text(user_note)

        if action == FeedbackAction.CONFIRMED.value:
            candidate.status = FeedbackAction.CONFIRMED.value
            self._update_judgement_status(
                snapshot=snapshot,
                judgement_id=candidate.source_judgement_id,
                status=ItemStatus.CONFIRMED.value,
            )
        elif action == FeedbackAction.REJECTED.value:
            candidate.status = FeedbackAction.REJECTED.value
            self._update_judgement_status(
                snapshot=snapshot,
                judgement_id=candidate.source_judgement_id,
                status=ItemStatus.QUESTIONED.value,
            )
        elif action == FeedbackAction.REVISED.value:
            candidate.status = FeedbackAction.REVISED.value
            self._update_judgement_status(
                snapshot=snapshot,
                judgement_id=candidate.source_judgement_id,
                status=ItemStatus.UNDER_REVISION.value,
            )
        else:
            return new_state

        new_state.stage_runtime.last_feedback_event = {
            "candidate_id": candidate_id,
            "action": action,
            "user_note": candidate.user_note,
        }

        new_state.stage_runtime.has_blocking_confirmation = self._detect_blocking_pending(snapshot)
        new_state.stage_runtime.current_maturity = self.infer_maturity_from_snapshot(snapshot)
        new_state.stage_runtime.can_transition = self._can_transition(
            maturity=new_state.stage_runtime.current_maturity,
            has_blocking_confirmation=new_state.stage_runtime.has_blocking_confirmation,
        )
        new_state.stage_runtime.next_prompt_hint = self._next_hint_after_feedback(action)

        return new_state

    def _find_candidate(
        self,
        snapshot: StageSnapshot,
        candidate_id: str,
    ) -> Optional[ConfirmationCandidate]:
        for item in snapshot.confirmation_candidates:
            if item.id == candidate_id:
                return item
        return None

    def _update_judgement_status(
        self,
        snapshot: StageSnapshot,
        judgement_id: str,
        status: str,
    ) -> None:
        for item in snapshot.judgements:
            if item.id == judgement_id:
                item.status = status
                return

    def _next_hint_after_feedback(self, action: str) -> str:
        if action == FeedbackAction.CONFIRMED.value:
            return "承接已确认判断，优先向前推进"
        if action == FeedbackAction.REJECTED.value:
            return "先修正当前判断，不要沿原方向继续叠加"
        if action == FeedbackAction.REVISED.value:
            return "优先吸收用户补充，再更新当前判断"
        return "继续当前阶段"

    # -------------------------
    # 阶段切换
    # -------------------------

    def transition_to_next_stage(self, stage_state: StageState) -> Optional[StageState]:
        """
        切换到下一个阶段
        """
        runtime = stage_state.stage_runtime
        if not runtime.can_transition:
            return None

        next_stage = self.method_definition.get_next_stage(stage_state.stage_definition.stage_id)
        if next_stage is None:
            completed_state = deepcopy(stage_state)
            completed_state.stage_runtime.status = StageRunStatus.COMPLETED.value
            return completed_state

        snapshot = StageSnapshot(
            method_id=self.method_definition.method_id,
            stage_id=next_stage.stage_id,
            stage_name=next_stage.stage_name,
            stage_summary="",
            findings=[],
            judgements=[],
            confirmation_candidates=[],
            next_prompt_hint="开始新阶段的探索",
        )

        runtime = StageRuntime(
            current_maturity=MaturityLevel.L0.value,
            stage_snapshot=snapshot,
            can_transition=False,
            has_blocking_confirmation=False,
            last_feedback_event=None,
            next_prompt_hint=snapshot.next_prompt_hint,
            status=StageRunStatus.ACTIVE.value,
        )

        return StageState(
            stage_definition=next_stage,
            stage_runtime=runtime,
        )

    # -------------------------
    # 恢复快照
    # -------------------------

    def build_resume_snapshot(
        self,
        conversation_id: str,
        stage_state: StageState,
    ) -> ConversationResumeSnapshot:
        return ConversationResumeSnapshot(
            conversation_id=conversation_id,
            method_id=self.method_definition.method_id,
            current_stage_id=stage_state.stage_definition.stage_id,
            current_stage_maturity=stage_state.stage_runtime.current_maturity,
            stage_snapshot=deepcopy(stage_state.stage_runtime.stage_snapshot),
            has_blocking_pending_confirmation=stage_state.stage_runtime.has_blocking_confirmation,
            next_prompt_hint=stage_state.stage_runtime.next_prompt_hint,
            last_feedback_event=deepcopy(stage_state.stage_runtime.last_feedback_event),
        )

    # -------------------------
    # 历史阶段挑战（先记事件，不直接改）
    # -------------------------

    def apply_historical_revision_event(
        self,
        historical_stage_snapshot: StageSnapshot,
        judgement_id: str,
        user_note: str = "",
    ) -> StageSnapshot:
        """
        历史阶段允许被挑战，但不允许被直接编辑：
        这里只把对应 judgement 标成 questioned / under_revision
        """
        snapshot = deepcopy(historical_stage_snapshot)
        note = self._clean_text(user_note)

        for judgement in snapshot.judgements:
            if judgement.id == judgement_id:
                judgement.status = ItemStatus.QUESTIONED.value
                break

        for candidate in snapshot.confirmation_candidates:
            if candidate.source_judgement_id == judgement_id:
                candidate.status = ItemStatus.UNDER_REVISION.value
                candidate.user_note = note

        return snapshot

    # -------------------------
    # 工具方法
    # -------------------------

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:10]}"

    def _clean_text(self, text: Any) -> str:
        return str(text or "").strip()


# =========================
# SelfValue 示例方法论定义
# =========================

def build_self_value_method_definition() -> MethodDefinition:
    return MethodDefinition(
        method_id="self_value.main",
        method_name="Self Value",
        stages=[
            StageDefinition(
                stage_id="discovery",
                stage_name="价值挖掘",
                stage_goal="识别用户的独特价值资产与核心价值线索",
                coverage_scope=["能力", "热情", "市场验证"],
                output_direction=["价值线索归纳", "初步甜蜜点判断"],
            ),
            StageDefinition(
                stage_id="design",
                stage_name="模式构建",
                stage_goal="把价值线索转成更清晰的商业结构",
                coverage_scope=["价值主张", "客户细分", "收入模式", "关键活动"],
                output_direction=["初步价值主张", "商业模式方向"],
            ),
            StageDefinition(
                stage_id="validate",
                stage_name="验证与迭代",
                stage_goal="降低风险并形成最小验证路径",
                coverage_scope=["MVP", "反馈收集", "pivot 条件"],
                output_direction=["验证方案", "优先验证点"],
            ),
            StageDefinition(
                stage_id="optimize",
                stage_name="持续优化",
                stage_goal="建立长期复盘与优化机制",
                coverage_scope=["复盘", "校准", "升级路径"],
                output_direction=["优化机制", "阶段行动方向"],
            ),
        ],
    )


# =========================
# 用法示例（可删）
# =========================

if __name__ == "__main__":
    method_def = build_self_value_method_definition()
    stage_layer = StageLayer(method_definition=method_def)

    # 初始化
    stage_state = stage_layer.create_initial_stage_state()
    print("初始化阶段：")
    print(stage_state.to_dict())

    # 模拟一个阶段原始产出
    raw_output = RawStageOutput(
        stage_summary="这一阶段已经初步识别出用户更强的价值线索与高能量方向。",
        raw_findings=[
            "用户多次提到自己擅长快速看清问题关键",
            "用户对重复执行型工作有明显抗拒",
            "用户在帮助别人梳理方向时更容易感到有能量",
        ],
        raw_judgements=[
            "用户当前更适合承担看清问题和梳理方向的角色，而不是长期执行推进的角色",
            "用户的价值线索更偏向认知梳理型输出，而不是事务型支持",
        ],
        next_prompt_hint="可以承接当前判断，继续确认其适合服务谁",
    )

    stage_state = stage_layer.update_stage_state_from_raw_output(stage_state, raw_output)
    print("\n更新后阶段状态：")
    print(stage_state.to_dict())

    # 模拟用户确认
    if stage_state.stage_runtime.stage_snapshot and stage_state.stage_runtime.stage_snapshot.confirmation_candidates:
        candidate_id = stage_state.stage_runtime.stage_snapshot.confirmation_candidates[0].id
        stage_state = stage_layer.apply_feedback(
            stage_state=stage_state,
            candidate_id=candidate_id,
            action=FeedbackAction.CONFIRMED.value,
        )
        print("\n用户确认后：")
        print(stage_state.to_dict())

    # 恢复快照
    resume_snapshot = stage_layer.build_resume_snapshot(
        conversation_id="conv_demo_001",
        stage_state=stage_state,
    )
    print("\n恢复快照：")
    print(resume_snapshot.to_dict())
