"""requirement_parser：穿搭需求解析。

输入：表单字段或自然语言文本（MVP 阶段以表单为主）。
输出：Requirements 结构化对象；预算一律以"分"保存。
"""

from __future__ import annotations

import re

from .models import Requirements, HardConstraints, SCENES, DEFAULT_BUDGET_FEN, gen_id


def parse_requirement(
    *,
    occasion: str = "",
    temperature_text: str = "",
    budget_yuan: float = 0.0,
    size_requirements: dict | None = None,
    exclude_colors=None,
    exclude_silhouettes=None,
    exclude_categories=None,
    soft_preferences: dict | None = None,
    natural_text: str = "",
) -> dict:
    """解析需求。返回 {"requirements": Requirements, "missing_required": [...], "conflicts": [...], "warnings": [...]}。"""
    missing = []
    conflicts = []
    warnings = []

    occasion = (occasion or "").strip()
    if occasion and occasion not in SCENES:
        conflicts.append(f"场景 {occasion!r} 不在支持范围内：{SCENES}")

    budget_fen = int(DEFAULT_BUDGET_FEN)
    if budget_yuan:
        try:
            budget_fen = int(round(float(budget_yuan) * 100))
        except (TypeError, ValueError):
            warnings.append("预算格式无法解析，使用默认值 500 元")

    if budget_fen <= 0:
        conflicts.append("预算必须为正数")

    sizes = {}
    for k, v in (size_requirements or {}).items():
        if k in ("上衣", "下装", "外套", "鞋类") and (v or "").strip():
            sizes[k] = v.strip()
        elif k == "包饰":
            sizes["包饰"] = "均码"

    hard = HardConstraints(
        exclude_colors=[c for c in (exclude_colors or []) if c],
        exclude_silhouettes=[s for s in (exclude_silhouettes or []) if s],
        exclude_categories=[c for c in (exclude_categories or []) if c],
        max_budget_fen=budget_fen,
    )
    req = Requirements(
        occasion=occasion or "",
        temperature_text=(temperature_text or "").strip(),
        budget_fen=budget_fen,
        size_requirements=sizes,
        hard=hard,
        soft_preferences=soft_preferences or {},
        missing_required=missing,
        conflicts=conflicts,
    )
    return {
        "requirements": req,
        "requirements_id": gen_id("req"),
        "missing_required": missing,
        "conflicts": conflicts,
        "warnings": warnings,
    }


def parse_natural_text(text: str, budget_yuan: float = 0.0) -> dict:
    """自然语言简单解析（仅提取场景与预算关键词；尺码仍需表单）。"""
    scene_map = {
        "上课": "上课与日常通勤",
        "通勤": "上课与日常通勤",
        "日常": "上课与日常通勤",
        "面试": "面试与答辩",
        "答辩": "面试与答辩",
        "社团": "社团活动与普通社交",
        "社交": "社团活动与普通社交",
        "聚会": "社团活动与普通社交",
    }
    occasion = ""
    for key, scene in scene_map.items():
        if key in text:
            occasion = scene
            break

    # 从文本提取预算：如 "预算400元" "300块" "预算 500"
    if not budget_yuan:
        m = re.search(r"预算[^\d]*(\d+(?:\.\d+)?)\s*(?:元|块)?", text)
        if not m:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:元|块)", text)
        if m:
            budget_yuan = float(m.group(1))

    return parse_requirement(
        occasion=occasion, budget_yuan=budget_yuan, natural_text=text
    )
