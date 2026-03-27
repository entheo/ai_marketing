"""
prompt_method_checker.py
========================

用途：
检查 raw prompt 是否具备基本的方法论协议质量，是否适合进入系统。

它检查的是：
1. 方法论目标是否可识别
2. 阶段推进逻辑是否可识别
3. 关键覆盖内容是否可识别
4. 阶段 / 流程产出方向是否可识别
5. 推荐项是否较完整
6. 是否存在越界混层问题

它不负责：
1. 修改 PromptAdapter
2. 修改 PromptRunner
3. 自动重写 raw prompt
4. 检查前端逻辑
5. 检查 JSON 输出协议正确性

设计原则：
- 软协议，不要求固定标题 / 固定顺序 / 固定字段名
- 检查“信息是否可识别”，不是检查“格式像不像模板”
- 第一版采用规则型 + 轻启发式语义判断
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# =========================
# 基础数据结构
# =========================

STATUS_CLEAR = "明确存在"
STATUS_WEAK = "弱存在"
STATUS_MISSING = "缺失"

BOUNDARY_NONE = "无越界"
BOUNDARY_LIGHT = "轻微越界"
BOUNDARY_HEAVY = "明显越界"


@dataclass
class CheckItemResult:
    name: str
    status: str
    reason: str
    suggestion: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class BoundaryItemResult:
    name: str
    status: str
    reason: str
    suggestion: str
    evidence: List[str] = field(default_factory=list)


# =========================
# 主检查器
# =========================

class PromptMethodChecker:
    """
    raw prompt 方法论检查器 v1
    """

    VERSION = "prompt_method_checker_v1"

    def __init__(self) -> None:
        self.required_rules = self._build_required_rules()
        self.recommended_rules = self._build_recommended_rules()
        self.boundary_rules = self._build_boundary_rules()

    # -------------------------
    # 对外主入口
    # -------------------------
    def check(
        self,
        raw_prompt: str,
        prompt_name: Optional[str] = None,
        prompt_id: Optional[str] = None
    ) -> Dict[str, Any]:
        text = self._normalize_text(raw_prompt)

        required_results = self._check_required_items(text)
        recommended_results = self._check_recommended_items(text)
        boundary_results = self._check_boundary_items(text)

        methodology_dimension = self._summarize_methodology_dimension(required_results)
        stage_dimension = self._summarize_stage_dimension(recommended_results, text)
        boundary_dimension = self._summarize_boundary_dimension(boundary_results)

        overall_grade, overall_comment, action_advice = self._grade(
            required_results=required_results,
            recommended_results=recommended_results,
            boundary_results=boundary_results
        )

        key_issues = self._build_key_issues(required_results, recommended_results, boundary_results)
        priority_suggestions = self._build_priority_suggestions(required_results, recommended_results, boundary_results)

        method_name = self._extract_method_name(text)

        result = {
            "basic_info": {
                "prompt_name": prompt_name or "",
                "prompt_id": prompt_id or "",
                "checked_at": datetime.now().isoformat(timespec="seconds"),
                "method_name": method_name or "",
                "checker_version": self.VERSION,
            },
            "overall_result": {
                "grade": overall_grade,
                "summary": overall_comment,
                "action": action_advice,
            },
            "dimensions": {
                "methodology_integrity": methodology_dimension,
                "stage_clarity": stage_dimension,
                "boundary_cleanliness": boundary_dimension,
            },
            "required_items": [self._item_to_dict(x) for x in required_results],
            "recommended_items": [self._item_to_dict(x) for x in recommended_results],
            "boundary_items": [self._boundary_to_dict(x) for x in boundary_results],
            "key_issues": key_issues[:3],
            "priority_suggestions": priority_suggestions[:3],
        }
        return result

    # -------------------------
    # 规则定义
    # -------------------------
    def _build_required_rules(self) -> Dict[str, Dict[str, Any]]:
        return {
            "method_goal": {
                "label": "方法论目标",
                "keywords_strong": [
                    "目标", "使命", "核心任务", "帮助用户", "帮助来访者", "最终帮助",
                    "帮助对方", "要完成", "想完成", "目的", "宗旨", "要让用户"
                ],
                "keywords_weak": [
                    "价值", "方向", "探索", "发现", "识别", "看清", "厘清", "梳理", "理解"
                ],
                "suggestion_weak": "当前方法论目标已有雏形，但表达仍偏分散，建议补清楚这套方法论最终帮助用户完成什么。",
                "suggestion_missing": "建议补充明确的方法论目标，否则系统难判断这套 raw prompt 到底在解决什么问题。"
            },
            "stage_progression": {
                "label": "阶段性推进逻辑",
                "keywords_strong": [
                    "阶段", "先", "再", "然后", "最后", "逐步", "推进", "收束",
                    "第一", "第二", "第三", "step", "phase", "流程", "路径"
                ],
                "keywords_weak": [
                    "从…到…", "探索", "聚焦", "判断", "建议", "总结", "归纳", "形成"
                ],
                "regex_strong": [
                    r"先.{0,20}再",
                    r"从.{0,30}到",
                    r"第一.{0,30}第二",
                    r"探索.{0,20}收束",
                ],
                "suggestion_weak": "当前已有推进痕迹，但阶段边界较弱，建议补充从探索到收束的大致推进路径。",
                "suggestion_missing": "建议补充阶段性推进逻辑，否则容易退化成随机聊天，方法论骨架不稳定。"
            },
            "coverage_scope": {
                "label": "关键覆盖内容",
                "keywords_strong": [
                    "覆盖", "维度", "方面", "核心问题", "问题域", "包括", "至少包括",
                    "需要关注", "重点看", "关键内容", "核心维度"
                ],
                "keywords_weak": [
                    "能力", "动机", "价值感", "身份感", "方向感", "资源", "限制",
                    "经历", "状态", "行为", "需求", "优势", "卡点"
                ],
                "suggestion_weak": "当前有部分覆盖方向，但核心问题域还不够显性，建议补清楚至少覆盖哪些核心维度。",
                "suggestion_missing": "建议补充关键覆盖内容，否则方法论容易只剩氛围，没有稳定的问题框架。"
            },
            "output_direction": {
                "label": "阶段 / 流程产出方向",
                "keywords_strong": [
                    "产出", "形成", "结果", "输出", "结论", "总结", "报告", "建议",
                    "判断", "发现", "方案", "收获", "沉淀"
                ],
                "keywords_weak": [
                    "看见", "识别出", "梳理出", "明确", "得到", "沉淀为"
                ],
                "suggestion_weak": "当前已有结果导向，但产出类型仍不够稳定，建议补清楚阶段或整体流程会形成什么类型结果。",
                "suggestion_missing": "建议补充阶段或整体流程的产出方向，否则系统难判断何时收束、收束成什么。"
            },
        }

    def _build_recommended_rules(self) -> Dict[str, Dict[str, Any]]:
        return {
            "stage_naming": {
                "label": "阶段名称清晰度",
                "keywords_strong": [
                    "阶段", "phase", "step", "第一阶段", "第二阶段", "模块", "部分", "环节"
                ],
                "keywords_weak": [
                    "先探索", "再聚焦", "最后收束", "前期", "中期", "后期"
                ],
                "suggestion_weak": "已有阶段感，但名称边界较弱，建议让阶段边界更容易被识别。",
                "suggestion_missing": "建议补出更清楚的阶段名称或阶段边界，便于后续系统理解流程位置。"
            },
            "stage_goals": {
                "label": "每阶段目标可见性",
                "keywords_strong": [
                    "本阶段目标", "这一阶段要", "这一阶段重点", "这一阶段不是",
                    "阶段目标", "此阶段主要"
                ],
                "keywords_weak": [
                    "先做什么", "再做什么", "重点在", "先不要", "此时需要"
                ],
                "suggestion_weak": "已有阶段任务感，但每阶段目标还不够独立，建议把阶段目标说得更可见。",
                "suggestion_missing": "建议补出每阶段目标，否则阶段虽存在，也可能只剩顺序而没有方法论功能。"
            },
            "method_constraints": {
                "label": "方法论约束明确度",
                "keywords_strong": [
                    "一次只问一个问题", "不要直接给答案", "先探索再建议", "不要急于判断",
                    "避免", "禁止", "必须", "应当", "约束", "原则"
                ],
                "keywords_weak": [
                    "慢一点", "逐步", "先理解", "不急着建议", "谨慎判断", "少假设"
                ],
                "suggestion_weak": "已有一些工作原则，但还不够稳定，建议补充关键方法论约束。",
                "suggestion_missing": "建议补充关键方法论约束，否则执行风格容易漂移。"
            },
            "stage_outputs": {
                "label": "阶段级产出清晰度",
                "keywords_strong": [
                    "本阶段产出", "阶段产出", "该阶段形成", "这一阶段输出",
                    "中间结果", "阶段结论"
                ],
                "keywords_weak": [
                    "先形成初步判断", "先得到线索", "阶段性总结", "中间收束"
                ],
                "suggestion_weak": "已有阶段性收束痕迹，但阶段产出还不够明确，建议补清楚中间会形成什么。",
                "suggestion_missing": "建议补充阶段级产出方向，否则流程中间难以形成稳定抓手。"
            },
            "translatability": {
                "label": "阶段产出可转译性",
                "keywords_strong": [
                    "线索", "发现", "判断", "假设", "结论", "finding", "judgement",
                    "insight", "theme", "signal"
                ],
                "keywords_weak": [
                    "归纳", "提炼", "总结为", "沉淀为", "结构化"
                ],
                "suggestion_weak": "已有可转译倾向，但对象化程度偏弱，建议让阶段结果更容易转成中间对象。",
                "suggestion_missing": "建议补充阶段结果的可转译性，让后续更容易沉淀为 finding / judgement 一类中间对象。"
            },
        }

    def _build_boundary_rules(self) -> Dict[str, Dict[str, Any]]:
        return {
            "product_display": {
                "label": "产品展示规则越界",
                "keywords_heavy": [
                    "右侧展示", "点击查看", "用户点击", "展示几条", "展示卡片", "可点击",
                    "前端展示", "页面展示", "按钮", "tab", "组件", "卡片", "UI"
                ],
                "keywords_light": [
                    "呈现给用户", "展示给用户", "显示", "可见", "界面"
                ],
                "suggestion_light": "建议去掉 raw prompt 中偏产品展示层的表达，只保留方法论本身。",
                "suggestion_heavy": "raw prompt 中混入了明显的产品展示规则，建议整体移出到产品层或前端层。"
            },
            "interaction_state": {
                "label": "交互状态规则越界",
                "keywords_heavy": [
                    "confirmation_candidate", "blocking", "non_blocking", "用户不点怎么办",
                    "反馈回流", "确认态", "交互状态", "状态切换", "点击确认", "回流机制"
                ],
                "keywords_light": [
                    "确认", "等待用户确认", "用户反馈", "继续或停止"
                ],
                "suggestion_light": "建议去掉 raw prompt 中偏交互状态层的规则，避免方法论层与交互层混写。",
                "suggestion_heavy": "raw prompt 中混入了明显的交互状态逻辑，建议整体迁出到系统流程层。"
            },
            "engineering_protocol": {
                "label": "工程输出协议越界",
                "keywords_heavy": [
                    "json", "status", "枚举", "字段", "schema", "PromptAdapter",
                    "PromptRunner", "输出协议", "字段结构", "response format", "parser"
                ],
                "keywords_light": [
                    "结构化输出", "固定字段", "按字段返回", "返回对象"
                ],
                "suggestion_light": "建议减少 raw prompt 中工程协议表达，只保留方法论想形成的结果方向。",
                "suggestion_heavy": "raw prompt 中混入了明显的工程输出协议，建议迁移到适配层或运行层。"
            },
        }

    # -------------------------
    # 必需项检查
    # -------------------------
    def _check_required_items(self, text: str) -> List[CheckItemResult]:
        results = []
        for key, rule in self.required_rules.items():
            results.append(self._evaluate_item(rule, text))
        return results

    # -------------------------
    # 推荐项检查
    # -------------------------
    def _check_recommended_items(self, text: str) -> List[CheckItemResult]:
        results = []
        for key, rule in self.recommended_rules.items():
            results.append(self._evaluate_item(rule, text))
        return results

    # -------------------------
    # 越界项检查
    # -------------------------
    def _check_boundary_items(self, text: str) -> List[BoundaryItemResult]:
        results = []

        for key, rule in self.boundary_rules.items():
            heavy_hits = self._find_hits(text, rule.get("keywords_heavy", []))
            light_hits = self._find_hits(text, rule.get("keywords_light", []))

            if heavy_hits:
                status = BOUNDARY_HEAVY
                reason = f"检测到明显越界表达：{self._join_evidence(heavy_hits)}。"
                suggestion = rule["suggestion_heavy"]
                evidence = heavy_hits[:5]
            elif len(light_hits) >= 2:
                status = BOUNDARY_LIGHT
                reason = f"检测到一定越界倾向：{self._join_evidence(light_hits)}。"
                suggestion = rule["suggestion_light"]
                evidence = light_hits[:5]
            elif len(light_hits) == 1:
                status = BOUNDARY_LIGHT
                reason = f"存在轻微越界迹象：{self._join_evidence(light_hits)}。"
                suggestion = rule["suggestion_light"]
                evidence = light_hits[:5]
            else:
                status = BOUNDARY_NONE
                reason = "未检测到明显越界内容。"
                suggestion = "保持当前层级边界即可。"
                evidence = []

            results.append(
                BoundaryItemResult(
                    name=rule["label"],
                    status=status,
                    reason=reason,
                    suggestion=suggestion,
                    evidence=evidence
                )
            )

        return results

    # -------------------------
    # 单项判断
    # -------------------------
    def _evaluate_item(self, rule: Dict[str, Any], text: str) -> CheckItemResult:
        strong_hits = self._find_hits(text, rule.get("keywords_strong", []))
        weak_hits = self._find_hits(text, rule.get("keywords_weak", []))
        regex_hits = self._find_regex_hits(text, rule.get("regex_strong", []))

        strong_score = len(strong_hits) + len(regex_hits)
        weak_score = len(weak_hits)

        if strong_score >= 2:
            status = STATUS_CLEAR
            reason = f"可识别到较明确线索：{self._join_evidence(strong_hits + regex_hits)}。"
            suggestion = "当前项基本清楚，可保持。"
            evidence = (strong_hits + regex_hits)[:5]
        elif strong_score >= 1 or weak_score >= 3:
            status = STATUS_WEAK
            reason = f"存在一定线索，但仍偏分散：{self._join_evidence(strong_hits + weak_hits + regex_hits)}。"
            suggestion = rule["suggestion_weak"]
            evidence = (strong_hits + weak_hits + regex_hits)[:5]
        else:
            status = STATUS_MISSING
            reason = "当前文本中难以识别出稳定线索。"
            suggestion = rule["suggestion_missing"]
            evidence = []

        return CheckItemResult(
            name=rule["label"],
            status=status,
            reason=reason,
            suggestion=suggestion,
            evidence=evidence
        )

    # -------------------------
    # 三大维度总结
    # -------------------------
    def _summarize_methodology_dimension(self, required_results: List[CheckItemResult]) -> Dict[str, Any]:
        counts = self._count_status(required_results)
        summary = self._build_dimension_summary(
            clear_count=counts[STATUS_CLEAR],
            weak_count=counts[STATUS_WEAK],
            missing_count=counts[STATUS_MISSING],
            dimension_name="方法论完整度"
        )
        return {
            "status": summary["status"],
            "reason": summary["reason"],
            "details": {
                "clear": counts[STATUS_CLEAR],
                "weak": counts[STATUS_WEAK],
                "missing": counts[STATUS_MISSING],
            }
        }

    def _summarize_stage_dimension(self, recommended_results: List[CheckItemResult], text: str) -> Dict[str, Any]:
        subset_names = {"阶段名称清晰度", "每阶段目标可见性", "阶段级产出清晰度"}
        subset = [x for x in recommended_results if x.name in subset_names]

        counts = self._count_status(subset)
        summary = self._build_dimension_summary(
            clear_count=counts[STATUS_CLEAR],
            weak_count=counts[STATUS_WEAK],
            missing_count=counts[STATUS_MISSING],
            dimension_name="阶段清晰度"
        )

        return {
            "status": summary["status"],
            "reason": summary["reason"],
            "details": {
                "clear": counts[STATUS_CLEAR],
                "weak": counts[STATUS_WEAK],
                "missing": counts[STATUS_MISSING],
            }
        }

    def _summarize_boundary_dimension(self, boundary_results: List[BoundaryItemResult]) -> Dict[str, Any]:
        none_count = sum(1 for x in boundary_results if x.status == BOUNDARY_NONE)
        light_count = sum(1 for x in boundary_results if x.status == BOUNDARY_LIGHT)
        heavy_count = sum(1 for x in boundary_results if x.status == BOUNDARY_HEAVY)

        if heavy_count >= 1:
            status = "边界不干净"
            reason = "存在明显混层问题，raw prompt 已部分越界到产品层、交互层或工程层。"
        elif light_count >= 1:
            status = "基本干净"
            reason = "整体边界尚可，但已有轻微混层痕迹，建议尽早清理。"
        else:
            status = "边界干净"
            reason = "未见明显混层问题，层级相对稳定。"

        return {
            "status": status,
            "reason": reason,
            "details": {
                "no_boundary_issue": none_count,
                "light_boundary_issue": light_count,
                "heavy_boundary_issue": heavy_count,
            }
        }

    # -------------------------
    # 总评判定
    # -------------------------
    def _grade(
        self,
        required_results: List[CheckItemResult],
        recommended_results: List[CheckItemResult],
        boundary_results: List[BoundaryItemResult]
    ) -> Tuple[str, str, str]:
        required_counts = self._count_status(required_results)
        recommended_counts = self._count_status(recommended_results)
        heavy_boundary = sum(1 for x in boundary_results if x.status == BOUNDARY_HEAVY)
        light_boundary = sum(1 for x in boundary_results if x.status == BOUNDARY_LIGHT)

        missing_required = required_counts[STATUS_MISSING]
        weak_required = required_counts[STATUS_WEAK]
        clear_required = required_counts[STATUS_CLEAR]
        clear_recommended = recommended_counts[STATUS_CLEAR]

        # D：底线明显不足
        if missing_required >= 2:
            return (
                "D",
                "方法论骨架不足，当前 raw prompt 还不适合直接接入系统。",
                "先重构"
            )

        # C：底线勉强，但结构不稳
        if missing_required == 1:
            return (
                "C",
                "已有部分方法论基础，但仍缺关键骨架，不建议直接接入。",
                "先整理"
            )

        # C：越界严重
        if heavy_boundary >= 2:
            return (
                "C",
                "方法论基础存在，但混层明显，当前版本不建议直接接入。",
                "先整理"
            )

        # B：可用但建议补强
        if clear_required >= 3 and heavy_boundary == 0:
            if clear_recommended >= 3 and light_boundary == 0:
                return (
                    "A",
                    "方法论骨架较完整，层级也较干净，可直接接入。",
                    "可直接接入"
                )
            return (
                "B",
                "方法论底线基本成立，但阶段清晰度或约束表达仍可加强。",
                "补强后接入"
            )

        # 默认 B / C 之间偏保守
        if weak_required >= 2 or light_boundary >= 1:
            return (
                "B",
                "基本可用，但仍建议补清关键方法论信息后再接入。",
                "补强后接入"
            )

        return (
            "C",
            "当前 raw prompt 结构仍偏松散，建议先整理后再考虑接入。",
            "先整理"
        )

    # -------------------------
    # 关键问题 / 优先建议
    # -------------------------
    def _build_key_issues(
        self,
        required_results: List[CheckItemResult],
        recommended_results: List[CheckItemResult],
        boundary_results: List[BoundaryItemResult]
    ) -> List[str]:
        issues: List[str] = []

        for item in required_results:
            if item.status == STATUS_MISSING:
                issues.append(f"必需项缺失：{item.name}。")
        for item in required_results:
            if item.status == STATUS_WEAK:
                issues.append(f"必需项偏弱：{item.name}。")
        for item in boundary_results:
            if item.status == BOUNDARY_HEAVY:
                issues.append(f"明显越界：{item.name}。")
        for item in recommended_results:
            if item.status == STATUS_MISSING:
                issues.append(f"推荐项不足：{item.name}。")

        if not issues:
            issues.append("未发现明显结构性问题。")

        return issues[:3]

    def _build_priority_suggestions(
        self,
        required_results: List[CheckItemResult],
        recommended_results: List[CheckItemResult],
        boundary_results: List[BoundaryItemResult]
    ) -> List[str]:
        suggestions: List[str] = []

        # 先必需项
        for item in required_results:
            if item.status in (STATUS_MISSING, STATUS_WEAK):
                suggestions.append(item.suggestion)

        # 再越界
        for item in boundary_results:
            if item.status in (BOUNDARY_HEAVY, BOUNDARY_LIGHT):
                suggestions.append(item.suggestion)

        # 最后推荐项
        for item in recommended_results:
            if item.status in (STATUS_MISSING, STATUS_WEAK):
                suggestions.append(item.suggestion)

        # 去重，保持顺序
        deduped = []
        seen = set()
        for s in suggestions:
            if s not in seen:
                deduped.append(s)
                seen.add(s)

        if not deduped:
            deduped.append("当前 raw prompt 整体可用，后续主要保持方法论边界与阶段清晰度即可。")

        return deduped[:3]

    # -------------------------
    # 工具方法
    # -------------------------
    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _find_hits(self, text: str, keywords: List[str]) -> List[str]:
        hits = []
        lower_text = text.lower()

        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in lower_text:
                hits.append(kw)
        return hits

    def _find_regex_hits(self, text: str, patterns: List[str]) -> List[str]:
        hits = []
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
                hits.append(pattern)
        return hits

    def _join_evidence(self, evidence: List[str]) -> str:
        if not evidence:
            return "无明显线索"
        return "、".join(evidence[:4])

    def _count_status(self, items: List[CheckItemResult]) -> Dict[str, int]:
        return {
            STATUS_CLEAR: sum(1 for x in items if x.status == STATUS_CLEAR),
            STATUS_WEAK: sum(1 for x in items if x.status == STATUS_WEAK),
            STATUS_MISSING: sum(1 for x in items if x.status == STATUS_MISSING),
        }

    def _build_dimension_summary(
        self,
        clear_count: int,
        weak_count: int,
        missing_count: int,
        dimension_name: str
    ) -> Dict[str, str]:
        if missing_count >= 2:
            return {
                "status": "不足",
                "reason": f"{dimension_name}明显不足，缺少关键可识别信息。"
            }
        if missing_count == 1 or weak_count >= 2:
            return {
                "status": "一般",
                "reason": f"{dimension_name}已有基础，但仍偏松散，建议补强。"
            }
        return {
            "status": "较好",
            "reason": f"{dimension_name}整体较稳定，可识别性尚可。"
        }

    def _item_to_dict(self, item: CheckItemResult) -> Dict[str, Any]:
        return {
            "name": item.name,
            "status": item.status,
            "reason": item.reason,
            "suggestion": item.suggestion,
            "evidence": item.evidence,
        }

    def _boundary_to_dict(self, item: BoundaryItemResult) -> Dict[str, Any]:
        return {
            "name": item.name,
            "status": item.status,
            "reason": item.reason,
            "suggestion": item.suggestion,
            "evidence": item.evidence,
        }

    def _extract_method_name(self, text: str) -> str:
        patterns = [
            r"方法论名称[:：]\s*([^\n]{1,40})",
            r"名称[:：]\s*([^\n]{1,40})",
            r"你是[一位个名种类\w\s、，,：:《》\-]{0,20}(.{2,20})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                name = match.group(1).strip(" ：:，,。.;；")
                if 1 < len(name) <= 40:
                    return name
        return ""



# =========================
# 命令行入口
# =========================

def check_prompt(
    raw_prompt: str,
    prompt_name: Optional[str] = None,
    prompt_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    供外部直接调用的函数
    """
    checker = PromptMethodChecker()
    return checker.check(
        raw_prompt=raw_prompt,
        prompt_name=prompt_name,
        prompt_id=prompt_id
    )


def main() -> None:
    """
    简单 CLI 用法：
    python prompt_method_checker.py input.txt
    或：
    python prompt_method_checker.py
    然后手动粘贴 raw prompt，Ctrl+D / Ctrl+Z 结束
    """
    import sys

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
        with open(input_path, "r", encoding="utf-8") as f:
            raw_prompt = f.read()
        prompt_name = input_path
    else:
        print("请输入 raw prompt，结束后按 Ctrl+D（Linux/macOS）或 Ctrl+Z（Windows）：")
        raw_prompt = sys.stdin.read()
        prompt_name = "stdin_input"

    result = check_prompt(
        raw_prompt=raw_prompt,
        prompt_name=prompt_name,
        prompt_id=""
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
