"""T5 验收测试：skills_lib 各模块边界用例。

运行: python tests/test_skills_lib.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from skills_lib import (  # noqa: E402
    load_catalog,
    filter_variants,
    plan_outfits,
    validate_plan,
    validate_all,
    parse_operation,
    apply_operation,
    build_shopping_list,
    build_board,
    audit_image,
    build_garment_card,
    parse_requirement,
    parse_natural_text,
    ClosetItem,
    Requirements,
    HardConstraints,
)

DATA = os.path.join(ROOT, "data", "inputs", "raw")
FAILED = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" | {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(name)


def demo_anchor():
    return ClosetItem(
        item_id="C001",
        user_id="u-demo",
        image_ref="demo://anchor-white-tee.jpg",
        category="上衣",
        primary_color="白色",
        pattern="纯色",
        silhouette="宽松",
        season_tags=["春", "夏"],
        style_tags=["休闲"],
        user_confirmed=True,
        available_status="available",
        source="demo",
    )


def demo_closets():
    return [
        ClosetItem(
            item_id="C002",
            user_id="u-demo",
            image_ref="demo://denim.jpg",
            category="下装",
            primary_color="深蓝",
            pattern="纯色",
            silhouette="直筒",
            season_tags=["春", "秋"],
            style_tags=["休闲"],
            user_confirmed=True,
            available_status="available",
        ),
        ClosetItem(
            item_id="C003",
            user_id="u-demo",
            image_ref="demo://shoes.jpg",
            category="鞋类",
            primary_color="白",
            silhouette=None,
            season_tags=["春", "夏", "秋"],
            style_tags=["休闲"],
            user_confirmed=True,
            available_status="available",
        ),
        ClosetItem(
            item_id="C004",
            user_id="u-demo",
            image_ref="demo://bad.jpg",
            category="外套",
            primary_color="黑",
            season_tags=["冬"],
            style_tags=["正式"],
            user_confirmed=True,
            available_status="lost",
        ),
    ]


def base_requirements():
    return Requirements(
        occasion="上课与日常通勤",
        budget_fen=50000,
        size_requirements={"上衣": "M", "下装": "L", "鞋类": "40"},
        hard=HardConstraints(max_budget_fen=50000),
    )


# ---------- 1. catalog_normalizer ----------
def test_catalog_normalizer():
    cat = load_catalog(os.path.join(DATA, "demo_products.csv"))
    check("normalizer: 30 products read", cat["total"] == 30, cat["total"])
    check("normalizer: 30 normalized", cat["normalized"] == 30, cat["normalized"])
    # 变体 57 条，其中 6 条无价格被拒
    check(
        "normalizer: 57 variants read",
        cat["variants_normalized"]
        + sum(1 for e in cat["errors"] if "价格" in e.get("reason", ""))
        == 57,
    )
    # 7 张 schema 中的产品数 = 30
    skus = {p.sku_id for p in cat["products"]}
    check("normalizer: sku uniqueness", len(skus) == 30)
    # M 码缺货的 V006 依然进入（normalizer 不判库存，由过滤层判）
    vids = {v.variant_id for v in cat["variants"]}
    check("normalizer: V006 present", "V006" in vids)
    return cat


# ---------- 2. privacy_audit ----------
def test_privacy_audit():
    r = audit_image("", mode="manual")
    check("privacy: missing image paused", not r["passed"])
    r = audit_image("", mode="demo")
    check(
        "privacy: demo passes without image",
        r["passed"] and "演示模式" in r["message"],
    )
    r = audit_image("demo://x.png", mode="manual", user_confirmed=False)
    check(
        "privacy: manual unconfirmed paused", not r["passed"] and r["action"] == "pause"
    )
    r = audit_image("demo://x.png", mode="manual", user_confirmed=True)
    check("privacy: manual confirmed continue", r["passed"])
    r = audit_image("demo://x.png", mode="demo")
    check("privacy: demo passes with note", r["passed"] and "演示模式" in r["message"])


# ---------- 3. garment_card ----------
def test_garment_card():
    bad = build_garment_card("x", source="user_input", user_input={"category": "帽子"})
    check("garment: invalid category rejected", not bad.get("valid"))
    good = build_garment_card(
        "x",
        source="user_input",
        user_input={
            "category": "上衣",
            "primary_color": "白",
            "silhouette": "宽松",
            "category_confidence": 0.9,
        },
    )
    check("garment: valid card", good.get("valid") and good["category"] == "上衣")
    demo = build_garment_card("x", source="demo", demo_item=demo_anchor())
    check("garment: demo card", demo.get("valid") and demo["source"] == "demo")


# ---------- 4. requirement_parser ----------
def test_requirement_parser():
    r = parse_requirement(
        occasion="面试与答辩",
        budget_yuan=300,
        size_requirements={"上衣": "M", "下装": "L"},
    )
    req = r["requirements"]
    check("req: budget in fen", req.budget_fen == 30000)
    check("req: no conflicts", not r["conflicts"])
    r2 = parse_requirement(occasion="海边度假", budget_yuan=-5)
    check("req: conflict detected", len(r2["conflicts"]) >= 1)
    r3 = parse_natural_text("我要去面试，预算400元")
    check("req: natural text scene", r3["requirements"].occasion == "面试与答辩")
    check("req: natural text budget", r3["requirements"].budget_fen == 40000)


# ---------- 5. hard_constraint_filter ----------
def test_constraint_filter(cat):
    req = base_requirements()
    fr = filter_variants(cat["products"], cat["variants"], req)
    passed_ids = [v.variant_id for v in fr["passed"]]
    # V006 (M码缺货) 必须被排除
    check("filter: V006 excluded (M out of stock)", "V006" not in passed_ids)
    # V008/V009（无价格）不会出现在商品中——它们已被 normalizer 拒绝，所以自然不在 variants 里；此处验证无价格变体不在 passed
    check(
        "filter: no price-missing variant passed",
        all(v.price_fen >= 0 for v in fr["passed"]),
    )
    # 下架商品 OW-BTM-003 的任何变体都不应通过
    off_skus = {"OW-BTM-003", "OW-OUT-006", "OW-ACC-003"}
    pid2sku = {}
    for p in cat["products"]:
        pid2sku[p.product_id] = p.sku_id
    bad_sku = [
        pid2sku.get(v.product_id)
        for v in fr["passed"]
        if pid2sku.get(v.product_id) in off_skus
    ]
    check("filter: off-shelf/discontinued excluded", not bad_sku, bad_sku)
    # Oversize 排除
    req.hard.exclude_silhouettes = ["Oversize"]
    fr2 = filter_variants(cat["products"], cat["variants"], req)
    ov_skus = [
        pid2sku.get(v.product_id)
        for v in fr2["passed"]
        if pid2sku.get(v.product_id) == "OW-TOP-006"
    ]
    check("filter: oversize excluded", "OW-TOP-006" not in ov_skus)
    # 预算 300 元：OW-OUT-004 599 元应被排除
    req2 = base_requirements()
    req2.hard.max_budget_fen = 30000
    fr3 = filter_variants(cat["products"], cat["variants"], req2)
    over = [v for v in fr3["passed"] if v.price_fen > 30000]
    check("filter: over-budget excluded", not over, [o.variant_id for o in over])
    return fr


# ---------- 6. planner ----------
def test_planner(cat, fr):
    req = base_requirements()
    anchor = demo_anchor()
    result = plan_outfits(
        anchor=anchor,
        closet_items=demo_closets(),
        products=cat["products"],
        variants=cat["variants"],
        requirements=req,
        filter_result=fr,
    )
    check("planner: at least 1 plan", result["plan_count"] >= 1, result["plan_count"])
    check("planner: <=3 plans", result["plan_count"] <= 3)
    for p in result["plans"]:
        # 锚点必须出现
        roles = [i.role for i in p.items]
        check(f"planner: anchor in {p.plan_label}", "上衣" in roles)
        # 每套 <=5 件
        check(f"planner: {p.plan_label} <=5 items", len(p.items) <= 5, len(p.items))
        # 预算校验
        check(
            f"planner: {p.plan_label} within budget",
            p.purchase_subtotal_fen <= req.hard.max_budget_fen,
            p.purchase_subtotal_fen,
        )
    # 方案互不相同
    sigs = {tuple(sorted((i.role, i.ref_id) for i in p.items)) for p in result["plans"]}
    check("planner: plans distinct", len(sigs) == result["plan_count"])
    return result


# ---------- 7. validator ----------
def test_validator(cat, result):
    req = base_requirements()
    results = validate_all(result["plans"], req)
    check(
        "validator: plan1 passed",
        results[0]["validation_status"] == "passed",
        results[0]["failed_reasons"],
    )
    # 构造超预算场景：手工构造一个含高价格商品且超出预算的方案
    from skills_lib.models import Plan, PlanItem, gen_id

    fake = Plan(
        plan_id=gen_id("plan"),
        plan_label="超预算测试",
        items=[
            PlanItem(
                source="merchant",
                role="上衣",
                ref_id="V001",
                sku_id="OW-TOP-001",
                variant_id="V001",
                product_name="高价上衣",
                category="上衣",
                size="M",
                price_fen=99900,
            ),
        ],
        purchase_subtotal_fen=99900,
    )
    r = validate_plan(fake, req)
    check(
        "validator: over-budget plan fails budget",
        "budget" in r["failed_reasons"],
        r["failed_reasons"],
    )


# ---------- 8. replanner ----------
def test_replanner(cat, fr, result):
    req = base_requirements()
    plan = result["plans"][0]

    op = parse_operation("把裤子换成便宜一点的")
    check(
        "replanner: parse replace role",
        op["type"] == "REPLACE_ROLE" and op["target_role"] == "下装",
    )
    op2 = parse_operation("不要黑色")
    check(
        "replanner: parse exclude attr",
        op2["type"] == "EXCLUDE_ATTRIBUTE" and op2["attribute"] == "黑色",
    )
    op3 = parse_operation("预算改成200元")
    check(
        "replanner: parse budget",
        op3["type"] == "SET_MAX_BUDGET" and op3["budget_yuan"] == 200.0,
    )
    op4 = parse_operation("随便吧")
    check("replanner: ambiguous op flagged", op4["ambiguous"] is True)

    r = apply_operation(
        op3,
        plan=plan,
        requirements=req,
        products=cat["products"],
        variants=cat["variants"],
        closet_items=demo_closets(),
        anchor=demo_anchor(),
    )
    check("replanner: budget applied", r["ok"] and req.hard.max_budget_fen == 20000)

    r2 = apply_operation(
        op2,
        plan=plan,
        requirements=req,
        products=cat["products"],
        variants=cat["variants"],
        closet_items=demo_closets(),
        anchor=demo_anchor(),
    )
    check("replanner: exclude applied", r2["ok"] and "黑色" in req.hard.exclude_colors)

    # 替换角色（若方案里有商家下装则替换，否则报"无需替换"也算行为正确）
    if any(i.source == "merchant" and i.role == "下装" for i in plan.items):
        r3 = apply_operation(
            op,
            plan=plan,
            requirements=req,
            products=cat["products"],
            variants=cat["variants"],
            closet_items=demo_closets(),
            anchor=demo_anchor(),
        )
        check("replanner: replace role ok", r3["ok"])

    r4 = apply_operation(
        parse_operation("重新生成"),
        plan=plan,
        requirements=req,
        products=cat["products"],
        variants=cat["variants"],
        closet_items=demo_closets(),
        anchor=demo_anchor(),
    )
    check("replanner: replan ok or fallback", r4["ok"] or r4.get("message"))


# ---------- 9. shopping_list ----------
def test_shopping_list(cat, result):
    req = base_requirements()
    plan = result["plans"][0]
    sl = build_shopping_list(plan, inventory_snapshot_at="2026-10-07T19:00:00")
    check("list: status is intention only", sl["status"] == "购物意向清单已生成")
    check(
        "list: closet separate",
        all(
            not any(p["sku_id"] == c["item_id"] for p in sl["purchase_items"])
            for c in sl["closet_items"]
        ),
    )
    total = sl["financial_summary"]["purchase_subtotal_fen"]
    check("list: subtotal matches plan", total == plan.purchase_subtotal_fen, total)
    # 有 5 个运费未知变体（V019/V020/V043/V044/V045），若方案含它们则 final 未定并给出正确消息
    if sl["financial_summary"]["unknown_fee_list"]:
        check(
            "list: unknown fee message",
            "仍需确认运费" in sl["financial_summary"]["message"],
        )
        check(
            "list: final not determined",
            not sl["financial_summary"]["final_amount_determined"],
        )
    else:
        print("  (本方案未命中运费未知变体，跳过未定金额用例)")
    check("list: disclaimer present", "购物意向" in sl["disclaimer"])


# ---------- 10. board_builder ----------
def test_board_builder(result):
    plan = result["plans"][0]
    b = build_board(plan)
    check(
        "board: degraded card_grid mode",
        b["board_type"] == "card_grid" and b["status"] == "degraded",
    )
    check("board: items match plan", len(b["items"]) == len(plan.items))
    for it in b["items"]:
        check("board: sponsor labeled", it["is_sponsor"] == (it["sponsor_label"] != ""))
    check("board: disclaimer", "示意图" in b["disclaimer"])


def main():
    cat = test_catalog_normalizer()
    test_privacy_audit()
    test_garment_card()
    test_requirement_parser()
    fr = test_constraint_filter(cat)
    result = test_planner(cat, fr)
    test_validator(cat, result)
    test_replanner(cat, fr, result)
    test_shopping_list(cat, result)
    test_board_builder(result)

    print("\n" + "=" * 50)
    if FAILED:
        print(f"FAILED: {len(FAILED)} cases -> {FAILED}")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
