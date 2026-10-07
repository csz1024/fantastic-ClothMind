"""garment_card_builder：衣物识别卡。

本地 MVP 未接入视觉识别服务时的诚实策略：
- source="user_input"：用户在前端表单中逐项填写衣物属性（类别/颜色/版型等），
  本模块只做结构化和校验，不声称是"AI 识别"。
- source="vision_service"：仅当部署环境提供识别回调时使用，并保留置信度。
- source="demo"：演示流水线的预设衣物。

输出卡片每字段附带来源与置信度，低置信字段进入 needs_user_confirmation。
"""

from __future__ import annotations

from typing import Callable, Optional

from .models import CATEGORIES, ClosetItem

VisionRecognizer = Optional[Callable[[str], dict]]


def build_garment_card(
    image_path: str,
    *,
    source: str = "user_input",
    user_input: Optional[dict] = None,
    demo_item: Optional[ClosetItem] = None,
    recognizer: VisionRecognizer = None,
    user_id: str = "u-demo",
) -> dict:
    if source == "vision_service" and recognizer is not None:
        try:
            raw = recognizer(image_path)
            return _normalize_card(raw, source="vision_service", user_id=user_id)
        except Exception as exc:
            return _error_card(f"视觉识别失败：{exc}")

    if source == "demo" and demo_item is not None:
        return _from_closet_item(demo_item, source="demo")

    if source == "user_input" and user_input:
        return _normalize_card(user_input, source="user_input", user_id=user_id)

    return _error_card("缺少衣物信息来源（user_input / demo / vision_service）。")


def _normalize_card(raw: dict, source: str, user_id: str) -> dict:
    category = raw.get("category", "")
    if category not in CATEGORIES:
        return _error_card(f"类别必须为 {CATEGORIES} 之一，收到：{category!r}")

    low_conf = []
    for k, v in raw.items():
        conf = raw.get(f"{k}_confidence")
        if isinstance(conf, (int, float)) and conf < 0.6:
            low_conf.append(k)

    card = {
        "item_id": _gen_id("closet"),
        "user_id": user_id,
        "category": category,
        "primary_color": raw.get("primary_color", ""),
        "secondary_colors": raw.get("secondary_colors", []),
        "pattern": raw.get("pattern"),
        "silhouette": raw.get("silhouette"),
        "material_guess": raw.get("material_guess", "unknown"),
        "season_tags": raw.get("season_tags", []),
        "style_tags": raw.get("style_tags", []),
        "source": source,
        "confidence_summary": {
            k: raw.get(f"{k}_confidence")
            for k in ["category", "color", "pattern", "silhouette", "material"]
            if raw.get(f"{k}_confidence") is not None
        },
        "needs_user_confirmation": bool(low_conf),
        "suggested_edits": [f"{k} 置信度较低，请确认" for k in low_conf],
        "valid": True,
    }
    return card


def _from_closet_item(item: ClosetItem, source: str) -> dict:
    return {
        "item_id": item.item_id,
        "user_id": item.user_id,
        "category": item.category,
        "primary_color": item.primary_color,
        "secondary_colors": item.secondary_colors,
        "pattern": item.pattern,
        "silhouette": item.silhouette,
        "material_guess": item.material_guess or "unknown",
        "season_tags": item.season_tags,
        "style_tags": item.style_tags,
        "source": source,
        "confidence_summary": {},
        "needs_user_confirmation": False,
        "suggested_edits": [],
        "valid": True,
    }


def _error_card(message: str) -> dict:
    return {"valid": False, "error": message}


def _gen_id(prefix: str) -> str:
    import random
    import string

    return (
        prefix
        + "-"
        + "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(12)
        )
    )
