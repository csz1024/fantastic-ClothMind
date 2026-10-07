"""interactive_replanner：交互式改搭。

支持操作：LOCK_ITEM / UNLOCK_ITEM / REPLACE_ROLE / EXCLUDE_ATTRIBUTE /
SET_MAX_BUDGET / SET_SIZE / REFRESH_INVENTORY / REPLAN。
规则：歧义先询问；改后重新检索、重新过滤、重新规划、重新校验；
缺货时保留有效锁定项，只替换失效商品。
"""

from __future__ import annotations

from .models import Requirements, Plan, Product, Variant, ClosetItem, gen_id
from .constraint_filter import filter_variants
from .planner import plan_outfits

OPERATIONS = [
    "LOCK_ITEM",
    "UNLOCK_ITEM",
    "REPLACE_ROLE",
    "EXCLUDE_ATTRIBUTE",
    "SET_MAX_BUDGET",
    "SET_SIZE",
    "REFRESH_INVENTORY",
    "REPLAN",
]


def parse_operation(user_message: str) -> dict:
    """解析自然语言操作为结构化指令。无法确定时设置 ambiguous=True。"""
    text = (user_message or "").strip()
    op = {
        "type": None,
        "ambiguous": True,
        "required_clarification": None,
        "system_understanding": "",
        "raw": text,
    }

    if not text:
        op["required_clarification"] = (
            "请说明你想怎么调整（例如：把裤子换成便宜一点的）"
        )
        return op

    # 锁定
    if any(k in text for k in ["锁定", "保留这件"]):
        op.update(
            {
                "type": "LOCK_ITEM",
                "ambiguous": False,
                "system_understanding": "锁定当前方案中的指定单品",
            }
        )
        return op
    # 解锁
    if any(k in text for k in ["解锁", "取消锁定"]):
        op.update(
            {
                "type": "UNLOCK_ITEM",
                "ambiguous": False,
                "system_understanding": "解锁指定单品",
            }
        )
        return op
    # 替换
    if any(k in text for k in ["替换", "换成", "换一个", "不要这个"]):
        role = _detect_role(text)
        op.update(
            {
                "type": "REPLACE_ROLE",
                "ambiguous": role is None,
                "target_role": role,
                "constraint": {},
                "system_understanding": f"替换方案中的「{role}」单品"
                if role
                else "需要确认要替换哪个品类",
            }
        )
        if role is None:
            op["required_clarification"] = (
                "请问要替换哪个品类？（上衣/下装/外套/鞋类/包饰）"
            )
        return op
    # 排除属性
    if "不要" in text or "排除" in text:
        attr = (
            text.replace("不要", "")
            .replace("排除", "")
            .replace("颜色的", "")
            .replace("颜色", "")
            .strip("，。 ,")
        )
        op.update(
            {
                "type": "EXCLUDE_ATTRIBUTE",
                "ambiguous": not bool(attr),
                "attribute": attr,
                "system_understanding": f"排除「{attr}」属性的商品"
                if attr
                else "需要确认要排除什么属性",
            }
        )
        if not attr:
            op["required_clarification"] = (
                "请问要排除什么？（例如：不要黑色、不要Oversize版型）"
            )
        return op
    # 预算
    if "预算" in text or "便宜" in text or "价格" in text:
        import re

        m = re.search(r"(\d+(?:\.\d+)?)\s*(元|块)?", text)
        op.update(
            {
                "type": "SET_MAX_BUDGET",
                "ambiguous": False,
                "budget_yuan": float(m.group(1)) if m else None,
                "system_understanding": f"将最高预算调整为 {m.group(1)} 元"
                if m
                else "调整预算上限",
            }
        )
        return op
    # 尺码
    if "尺码" in text or "码" in text:
        op.update(
            {
                "type": "SET_SIZE",
                "ambiguous": True,
                "system_understanding": "调整某品类的尺码",
                "required_clarification": "请问调整哪个品类到什么尺码？",
            }
        )
        return op

    op["required_clarification"] = (
        "无法识别操作意图，请用更明确的说法（例如：把上装换成黑色的）"
    )
    return op


def _detect_role(text: str):
    for role in ["上衣", "下装", "外套", "鞋类", "包饰", "裤子", "鞋", "包"]:
        if role in text:
            return {"裤子": "下装", "鞋": "鞋类", "包": "包饰"}.get(role, role)
    return None


def apply_operation(
    op: dict,
    *,
    plan: Plan,
    requirements: Requirements,
    products: list,
    variants: list,
    closet_items: list,
    anchor: ClosetItem | None = None,
) -> dict:
    """执行操作并重规划。返回 {ok, message, plan, requirements, ambiguity, new_plans}。"""
    otype = op.get("type")
    if otype not in OPERATIONS:
        return {"ok": False, "message": f"不支持的操作类型：{otype}"}

    if otype == "LOCK_ITEM":
        return _lock(plan, requirements)
    if otype == "UNLOCK_ITEM":
        return _unlock(plan, requirements)
    if otype == "REPLACE_ROLE":
        return _replace(
            op, plan, requirements, products, variants, closet_items, anchor
        )
    if otype == "EXCLUDE_ATTRIBUTE":
        return _exclude(op, requirements)
    if otype == "SET_MAX_BUDGET":
        return _set_budget(op, requirements)
    if otype == "SET_SIZE":
        return {
            "ok": False,
            "message": "尺码调整需要明确品类与目标尺码",
            "ambiguity": True,
        }
    if otype == "REFRESH_INVENTORY":
        return _refresh(plan, requirements, products, variants, closet_items, anchor)
    if otype == "REPLAN":
        return _replan(plan, requirements, products, variants, closet_items, anchor)
    return {"ok": False, "message": "未知操作"}


def _replan(plan, requirements, products, variants, closet_items, anchor):
    if anchor is None:
        return {"ok": False, "message": "缺少锚点衣物，无法重规划"}
    result = plan_outfits(
        anchor=anchor,
        closet_items=closet_items,
        products=products,
        variants=variants,
        requirements=requirements,
    )
    return {
        "ok": True,
        "message": "已按当前约束重新生成方案",
        "new_plans": result["plans"],
        "plan": result["plans"][0] if result["plans"] else None,
        "roles_missing": result["roles_missing"],
    }


def _lock(plan, requirements):
    return {
        "ok": True,
        "message": "请用户在页面选择要锁定的单品后再执行；MVP 由前端传入 lock_key",
        "ambiguity": True,
    }


def _unlock(plan, requirements):
    return {
        "ok": True,
        "message": "请用户在页面选择要解锁的单品后再执行；MVP 由前端传入 lock_key",
        "ambiguity": True,
    }


def _replace(op, plan, requirements, products, variants, closet_items, anchor):
    role = op.get("target_role")
    if not role:
        return {"ok": False, "message": "缺少目标品类", "ambiguity": True}
    cur = [i for i in plan.items if i.role == role and i.source == "merchant"]
    if not cur:
        return {
            "ok": False,
            "message": f"方案中「{role}」不是商家商品，无需替换",
            "ambiguity": False,
        }
    old_vid = cur[0].variant_id
    # 找同品类其它可用变体（排除当前已使用的）
    used = {i.variant_id for i in plan.items if i.source == "merchant"}
    used.discard(old_vid)
    prod_index = {p.sku_id: p for p in products}
    # 重新过滤拿到全部可用变体
    fr = filter_variants(products, variants, requirements)
    cands = [v for v in fr["passed"] if v.variant_id not in used]
    cand_prods = {}
    pid_to_sku = {p.product_id: p for p in products}
    for v in variants:
        p = pid_to_sku.get(v.product_id)
        if p:
            cand_prods[v.variant_id] = p
    cands_v = [
        v
        for v in cands
        if _on_sale(cand_prods.get(v.variant_id))
        and cand_prods[v.variant_id].category == role
    ]
    if not cands_v:
        return {
            "ok": False,
            "message": f"「{role}」没有可替换的备选商品",
            "ambiguity": False,
        }
    cands_v.sort(key=lambda v: v.price_fen)
    pick = cands_v[0]
    # 重建 plan 引用
    new_items = []
    for i in plan.items:
        if i.role == role and i.source == "merchant":
            new_items.append(_mk_item(pick, cand_prods.get(pick.variant_id), role))
        else:
            new_items.append(i)
    plan.items = new_items
    plan.purchase_subtotal_fen = sum(
        i.price_fen for i in new_items if i.source == "merchant"
    )
    from .validator import validate_plan

    plan.validation = validate_plan(plan, requirements)
    picked_prod = cand_prods.get(pick.variant_id)
    picked_name = picked_prod.product_name if picked_prod else ""
    return {
        "ok": True,
        "message": f"已将「{role}」替换为 {pick.variant_id}（{picked_name}）",
        "plan": plan,
        "ambiguity": False,
    }


def _mk_item(v, prod, role):
    from .planner import _variant_plan_item

    return _variant_plan_item(v, prod, role)


def _np():
    from .models import Product

    return Product(
        product_id="",
        merchant_id="",
        sku_id="",
        product_name="",
        category="",
        sale_status="on_sale",
    )


def _on_sale(prod) -> bool:
    """判断商品是否为在售状态（prod 可为 Product 对象或 None）。"""
    if prod is None:
        return False
    status = getattr(prod, "sale_status", "")
    if isinstance(status, dict):  # 兼容字典形态
        status = status.get("sale_status", "")
    return status == "on_sale"


def _exclude(op, requirements):
    attr = (op.get("attribute") or "").strip()
    if not attr:
        return {"ok": False, "message": "缺少排除属性", "ambiguity": True}
    requirements.hard.exclude_colors.append(attr)
    return {
        "ok": True,
        "message": f"已排除属性「{attr}」，后续方案将不再包含该属性",
        "requirements": requirements,
        "ambiguity": False,
    }


def _set_budget(op, requirements):
    y = op.get("budget_yuan")
    if not y or y <= 0:
        return {"ok": False, "message": "预算金额无效", "ambiguity": False}
    requirements.hard.max_budget_fen = int(round(y * 100))
    requirements.budget_fen = requirements.hard.max_budget_fen
    return {
        "ok": True,
        "message": f"预算已调整为 {y:g} 元",
        "requirements": requirements,
        "ambiguity": False,
    }


def _refresh(plan, requirements, products, variants, closet_items, anchor):
    """库存刷新：无效项移除后保留有效项重规划。"""
    return _replan(plan, requirements, products, variants, closet_items, anchor)
