"""window_board_builder：数字橱窗/搭配看板生成。

本地 MVP 无真实图片合成工具，按 skill 约定降级为「商品卡片网格」
（board_type="card_grid"），并在结果中注明降级；不声称生成了效果图。
产出可直接渲染的卡片网格数据结构。
"""

from __future__ import annotations

from .models import Plan, gen_id


def build_board(plan: Plan, *, image_loader=None) -> dict:
    """生成橱窗展示数据结构。image_loader 可用时尝试拼图，不可用则降级。"""
    items = []
    for i in plan.items:
        items.append(
            {
                "role": i.role,
                "source": "自有衣物" if i.source == "closet" else "商家商品",
                "name": i.product_name or "",
                "size": i.size or "（自有）",
                "color": i.color or "",
                "price_text": ""
                if i.source == "closet"
                else f"¥{i.price_fen / 100:.2f}",
                "image_ref": i.image_ref or "",
                "product_url": i.product_url or "",
                "is_sponsor": i.is_sponsor,
                "sponsor_label": "[赞助]" if i.is_sponsor else "",
            }
        )

    board = {
        "board_type": "card_grid",
        "board_id": gen_id("board"),
        "items": items,
        "status": "degraded",
        "note": "演示环境未接入图片合成工具，使用商品卡片网格展示（不构成上身效果图）。",
        "disclaimer": "搭配示意图不代表真实上身效果；面料、版型与实物可能存在差异。",
    }
    return board
