"""hard_constraint_filter：硬约束过滤（确定性逻辑）。

过滤顺序（严格，任一失败即整体不通过）：
1. sale_status == on_sale
2. 需求尺码存在
3. 该尺码库存 > 0
4. 价格存在（price_fen >= 0）
5. 未命中排除项（颜色/版型/类别）
6. 不超过预算（price_fen <= max_budget_fen）
7. 锁定项保留（锁定的 variant 必须通过，若违反其它约束则标记 conflict）

返回通过/未通过的 variant 级结果，附每项检查证据。
"""

from __future__ import annotations

from .models import Product, Variant, Requirements, SALE_ON_SALE


def filter_variants(
    products: list,
    variants: list,
    requirements: Requirements,
    product_index: dict | None = None,
    variant_index: dict | None = None,
) -> dict:
    """按硬约束过滤变体。传入产品与变体列表（或建立好索引）。"""
    if product_index is None:
        product_index = {p.product_id: p for p in products}
        # 兜底：部分厂商表用 sku_id 引用，加入 sku_id 索引
        for p in products:
            product_index.setdefault(p.sku_id, p)
    if variant_index is None:
        variant_index = {v.variant_id: v for v in variants}

    hard = requirements.hard
    lock_keys = set()
    for item in hard.locked_items:
        if item.get("source") == "merchant" and item.get("variant_id"):
            lock_keys.add(item["variant_id"])

    passed: list[Variant] = []
    details = []
    for v in variants:
        p = product_index.get(v.product_id)
        if p is None:
            details.append(
                _detail(
                    v, {"product_lookup": {"passed": False, "reason": "商品不存在"}}
                )
            )
            continue
        checks = {}

        checks["sale_status"] = {
            "passed": p.sale_status == SALE_ON_SALE,
            "reason": ""
            if p.sale_status == SALE_ON_SALE
            else f"销售状态 {p.sale_status}",
        }

        need_size = requirements.size_requirements.get(p.category, "")
        checks["size_available"] = {
            "passed": (not need_size) or (v.size_label == need_size),
            "reason": ""
            if (not need_size) or v.size_label == need_size
            else f"需求尺码{need_size}，实际{v.size_label}",
        }

        checks["stock_positive"] = {
            "passed": v.stock_qty > 0,
            "reason": "" if v.stock_qty > 0 else f"库存 {v.stock_qty}",
        }

        checks["price_exists"] = {
            "passed": v.price_fen >= 0,
            "reason": "" if v.price_fen >= 0 else "价格缺失",
        }

        color_hit = [c for c in (p.color_tags or []) if c in hard.exclude_colors]
        checks["exclude_color"] = {
            "passed": not color_hit,
            "reason": "" if not color_hit else f"命中排除颜色 {color_hit}",
        }

        sil_hit = p.silhouette in hard.exclude_silhouettes if p.silhouette else False
        checks["exclude_silhouette"] = {
            "passed": not sil_hit,
            "reason": "" if not sil_hit else f"命中排除版型 {p.silhouette}",
        }

        cat_hit = p.category in hard.exclude_categories
        checks["exclude_category"] = {
            "passed": not cat_hit,
            "reason": "" if not cat_hit else f"命中排除类别 {p.category}",
        }

        checks["budget"] = {
            "passed": v.price_fen <= hard.max_budget_fen,
            "reason": ""
            if v.price_fen <= hard.max_budget_fen
            else f"价格 {v.price_fen // 100} 元超预算",
        }

        checks["lock_honored"] = {"passed": True, "reason": ""}
        over = all(c["passed"] for c in checks.values())
        if v.variant_id in lock_keys:
            if not over:
                checks["lock_honored"] = {
                    "passed": True,
                    "reason": "锁定项保留但违反其它约束（冲突待人工确认）",
                }
                over = True  # 锁定项必须保留，标记冲突

        details.append(_detail(v, checks, product=product_index.get(v.product_id)))
        if over:
            passed.append(v)

    return {
        "total": len(variants),
        "passed": passed,
        "passed_count": len(passed),
        "failed_count": len(variants) - len(passed),
        "details": details,
    }


def _detail(v: Variant, checks: dict, product: Product | None = None) -> dict:
    return {
        "variant_id": v.variant_id,
        "sku_id": product.sku_id if product else None,
        "product_name": product.product_name if product else None,
        "checks": {
            k: {"passed": c["passed"], "reason": c.get("reason", "")}
            for k, c in checks.items()
        },
        "overall": all(c["passed"] for c in checks.values()),
    }
