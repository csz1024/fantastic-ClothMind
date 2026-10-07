"""outfit_planner：搭配组合规划（确定性组合 + 规则排序）。

策略：
1. 锚点衣物（用户上传/确认的那件）必须出现在每套方案中。
2. 优先复用用户衣橱中其他可用单品（减少购买）。
3. 再按角色补齐商家商品（已通过硬约束过滤的变体）。
4. 展示 ≥1 且 ≤3 套方案；每套 ≤5 件；赞助商品显著标识。
5. 方案不做"时尚性"自评；校验交给 constraint_validator。
"""

from __future__ import annotations

import random

from .models import (
    Product,
    Variant,
    ClosetItem,
    Requirements,
    Plan,
    PlanItem,
    CATEGORIES,
    MAX_PLAN_ITEMS,
    MAX_PLANS,
    gen_id,
)

# 角色顺序：优先补齐的品类顺序
ROLE_ORDER = ["上衣", "外套", "下装", "鞋类", "包饰"]


def plan_outfits(
    *,
    anchor: ClosetItem,
    closet_items: list,
    products: list,
    variants: list,
    requirements: Requirements,
    filter_result: dict | None = None,
) -> dict:
    """生成候选方案列表。

    filter_result 若提供，直接使用其 passed variants；否则内部重新按
    requirements.hard 过滤（需保证变体已标准化）。
    """
    variant_index = {v.variant_id: v for v in variants}
    product_index = {p.product_id: p for p in products}
    prod_by_variant = {}
    for v in variants:
        prod_by_variant[v.variant_id] = product_index.get(v.product_id)

    if filter_result is None:
        from .constraint_filter import filter_variants

        filter_result = filter_variants(products, variants, requirements)
    eligible = list(filter_result["passed"])

    # 衣橱可用单品（除锚点外）
    closet_usable = [
        c
        for c in closet_items
        if c.item_id != anchor.item_id and c.available_status == "available"
    ]

    # 按角色聚合可补商家商品
    by_category: dict[str, list[Variant]] = {}
    for v in eligible:
        p = prod_by_variant.get(v.variant_id)
        if p:
            by_category.setdefault(p.category, []).append(v)

    plans: list[Plan] = []

    # 方案 1：已有优先（尽量少买）
    p1 = _build_plan(
        label="已有优先",
        anchor=anchor,
        closet_usable=closet_usable,
        by_category=by_category,
        prod_by_variant=prod_by_variant,
        requirements=requirements,
        prefer_closet=True,
        exclude_sponsor_only=False,
    )
    if p1:
        plans.append(p1)

    # 方案 2：预算节省优先（商家中挑最便宜补齐角色）
    p2 = _build_plan(
        label="预算优先",
        anchor=anchor,
        closet_usable=closet_usable,
        by_category=by_category,
        prod_by_variant=prod_by_variant,
        requirements=requirements,
        prefer_closet=True,
        exclude_sponsor_only=True,
    )
    if p2 and not _same_plan(p1, p2):
        plans.append(p2)

    # 方案 3：风格表达优先（允许 1 件赞助商品为点缀，随机选一家商家商品）
    p3 = _build_plan(
        label="风格表达",
        anchor=anchor,
        closet_usable=closet_usable,
        by_category=by_category,
        prod_by_variant=prod_by_variant,
        requirements=requirements,
        prefer_closet=False,
        exclude_sponsor_only=False,
    )
    if p3 and not any(_same_plan(p, p3) for p in plans):
        plans.append(p3)

    plans = plans[:MAX_PLANS]

    filled_roles = set()
    for plan in plans:
        for it in plan.items:
            filled_roles.add(it.role)
    missing_roles = [r for r in ROLE_ORDER if r not in filled_roles]

    return {
        "plans": plans,
        "plan_count": len(plans),
        "roles_filled": sorted(filled_roles),
        "roles_missing": missing_roles,
        "closet_usage": sum(1 for p in plans for i in p.items if i.source == "closet"),
        "merchant_usage": sum(
            1 for p in plans for i in p.items if i.source == "merchant"
        ),
        "eligible_variant_count": len(eligible),
    }


def _build_plan(
    *,
    label,
    anchor,
    closet_usable,
    by_category,
    prod_by_variant,
    requirements,
    prefer_closet,
    exclude_sponsor_only,
) -> Plan | None:
    items: list[PlanItem] = []

    anchor_item = PlanItem(
        source="closet",
        role=anchor.category,
        ref_id=anchor.item_id,
        product_name=_closet_name(anchor),
        category=anchor.category,
        image_ref=anchor.image_ref,
        lock_key=f"closet:{anchor.item_id}",
    )
    items.append(anchor_item)

    used_closet_ids = {anchor.item_id}
    used_variants = set()

    # 锚点类别之外的衣橱单品
    for c in closet_usable:
        if len(items) >= MAX_PLAN_ITEMS:
            break
        if c.category in {i.role for i in items}:
            continue
        if prefer_closet:
            items.append(_closet_plan_item(c))
            used_closet_ids.add(c.item_id)

    # 用商家商品补齐剩余角色（预算内）
    for role in ROLE_ORDER:
        if len(items) >= MAX_PLAN_ITEMS:
            break
        if role in {i.role for i in items}:
            continue
        cands = by_category.get(role, [])
        pick = _pick_variant(
            cands,
            requirements,
            used_variants,
            prod_by_variant=prod_by_variant,
            exclude_sponsor=exclude_sponsor_only,
        )
        if pick is None:
            continue
        prod = prod_by_variant.get(pick.variant_id)
        items.append(_variant_plan_item(pick, prod, role))
        used_variants.add(pick.variant_id)

    if len(items) < 2:
        return None

    subtotal = sum(i.price_fen for i in items if i.source == "merchant")
    plan = Plan(
        plan_id=gen_id("plan"),
        plan_label=label,
        items=items,
        purchase_subtotal_fen=subtotal,
        reasoning=f"{label}：锚点{anchor.category} + {len([i for i in items if i.source == 'merchant'])}件商家单品，共{len(items)}件",
    )
    # 预算硬校验：超预算则该方案作废
    if plan.purchase_subtotal_fen > requirements.hard.max_budget_fen:
        return None
    return plan


def _pick_variant(
    cands,
    requirements,
    used_variants,
    prod_by_variant,
    exclude_sponsor,
) -> Variant | None:
    """从候选中选一个变体：优先锁定项，其次排除赞助（如要求）、按价格升序取首个有库存者。"""
    if not cands:
        return None
    locked = requirements.hard.locked_items
    locked_vids = {i.get("variant_id") for i in locked if i.get("source") == "merchant"}
    for c in cands:
        if c.variant_id in locked_vids and c.variant_id not in used_variants:
            return c
    fresh = [c for c in cands if c.variant_id not in used_variants]
    if not fresh:
        return None
    if exclude_sponsor:
        fresh = [c for c in fresh if not _is_sponsor(prod_by_variant.get(c.variant_id))]
        if not fresh:
            return None
    fresh_sorted = sorted(fresh, key=lambda v: v.price_fen)
    for c in fresh_sorted:
        if c.stock_qty > 0:
            return c
    return None


def _is_sponsor(prod):
    """判断商品是否为赞助商品。prod 可为 Product 对象或 None。"""
    return bool(prod and getattr(prod, "is_sponsor", False))


def _variant_plan_item(v: Variant, prod: Product | None, role: str) -> PlanItem:
    return PlanItem(
        source="merchant",
        role=role,
        ref_id=v.variant_id,
        sku_id=prod.sku_id if prod else None,
        product_id=v.product_id,
        variant_id=v.variant_id,
        product_name=prod.product_name if prod else "",
        category=role,
        size=v.size_label,
        color=v.color_label or "",
        price_fen=v.price_fen,
        image_ref=prod.image_ref if prod else None,
        product_url=prod.product_url if prod else None,
        lock_key=f"merchant:{v.variant_id}",
        is_sponsor=prod.is_sponsor if prod else False,
        shipping_fee_fen=v.shipping_fee_fen,
    )


def _closet_plan_item(c: ClosetItem) -> PlanItem:
    return PlanItem(
        source="closet",
        role=c.category,
        ref_id=c.item_id,
        product_name=_closet_name(c),
        category=c.category,
        size="",
        color=c.primary_color,
        image_ref=c.image_ref,
        lock_key=f"closet:{c.item_id}",
    )


def _closet_name(c: ClosetItem) -> str:
    return (
        f"{c.primary_color}{c.pattern or ''}{c.category}"
        if c.primary_color
        else f"自有{c.category}"
    )


def _same_plan(a: Plan | None, b: Plan | None) -> bool:
    if a is None or b is None:
        return False
    ka = sorted((i.role, i.ref_id) for i in a.items)
    kb = sorted((i.role, i.ref_id) for i in b.items)
    return ka == kb
