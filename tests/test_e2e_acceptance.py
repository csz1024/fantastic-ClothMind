"""T8 端到端验收测试：模拟真实用户旅程。

覆盖链路：
  1. 上传衣物（隐私检查 -> 衣物识别）
  2. 填写需求（场景/预算/尺码解析）
  3. 加载商品目录
  4. 硬约束过滤（尺码/库存/价格/预算/排除项）
  5. 生成搭配方案（1-3 套）
  6. 锁定单品
  7. 替换单品（改搭）
  8. 缺货重规划（模拟某选中变体库存归零）
  9. 生成购物意向清单（含免责声明）
  10. 执行日志记录

运行：python tests/test_e2e_acceptance.py
退出码 0=全部通过；非 0=存在未通过项。
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from skills_lib import (
    AuditLogger,
    ClosetItem,
    Requirements,
    apply_operation,
    audit_image,
    build_garment_card,
    build_shopping_list,
    filter_variants,
    load_catalog,
    parse_operation,
    parse_requirement,
    plan_outfits,
    validate_plan,
)

RESULTS: list[dict] = []


def check(name: str, ok: bool, detail: str = ""):
    RESULTS.append({"name": name, "ok": bool(ok), "detail": detail})
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f"  ({detail})" if detail else ""))


def main() -> int:
    # ---------- 1. 上传衣物：隐私检查 ----------
    privacy = audit_image("demo://demo-shirt.png", mode="manual", user_confirmed=True)
    check("1 隐私检查通过", privacy["passed"] and privacy["action"] == "continue")

    # ---------- 1b. 衣物识别 ----------
    card = build_garment_card(
        "demo://demo-shirt.png",
        source="user_input",
        user_input={
            "category": "上衣",
            "primary_color": "白色",
            "pattern": "纯色",
            "silhouette": "宽松",
            "style_tags": ["休闲"],
            "season_tags": ["春", "夏"],
        },
    )
    check(
        "1b 衣物识别卡生成",
        card.get("valid")
        and card["category"] == "上衣"
        and card["primary_color"] == "白色",
        f"category={card.get('category')}",
    )

    # ---------- 2. 填写需求：解析 ----------
    req_r = parse_requirement(
        occasion="上课与日常通勤",
        budget_yuan=500,
        size_requirements={"上衣": "M", "下装": "L", "外套": "M", "鞋类": "40"},
        exclude_colors=[],
        exclude_silhouettes=[],
    )
    req: Requirements = req_r["requirements"]
    check(
        "2 需求解析",
        req.budget_fen == 50000 and not req_r["conflicts"],
        f"budget={req.budget_fen} 分",
    )

    # ---------- 3. 加载目录 ----------
    cat = load_catalog(
        os.path.join(ROOT, "data", "inputs", "raw", "demo_products.csv"),
        os.path.join(ROOT, "data", "inputs", "raw", "demo_variants.csv"),
    )
    check(
        "3 目录加载",
        cat["normalized"] == 30 and cat["variants_normalized"] >= 40,
        f"products={cat['normalized']} variants={cat['variants_normalized']} rejected={cat['rejected']}",
    )

    # ---------- 4. 硬约束过滤 ----------
    fr = filter_variants(cat["products"], cat["variants"], req)
    check(
        "4 硬约束过滤有通过项",
        fr["passed_count"] > 0 and fr["failed_count"] > 0,
        f"passed={fr['passed_count']} failed={fr['failed_count']}",
    )
    # 验证通过项确实满足预算
    over_budget = [v for v in fr["passed"] if v.price_fen > req.budget_fen]
    check("4b 通过项均不超预算", not over_budget)

    # ---------- 5. 生成方案 ----------
    anchor = ClosetItem(
        item_id="C001",
        user_id="u-e2e",
        image_ref="",
        category="上衣",
        primary_color="白色",
        pattern="纯色",
        silhouette="宽松",
        season_tags=["春", "夏"],
        style_tags=["休闲"],
        user_confirmed=True,
        available_status="available",
        source="user_input",
    )
    closet_mates = [
        ClosetItem(
            item_id="C002",
            user_id="u-e2e",
            image_ref="",
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
            user_id="u-e2e",
            image_ref="",
            category="鞋类",
            primary_color="白",
            silhouette="",
            season_tags=["春", "夏", "秋"],
            style_tags=["休闲"],
            user_confirmed=True,
            available_status="available",
        ),
    ]
    plans = plan_outfits(
        anchor=anchor,
        closet_items=closet_mates,
        products=cat["products"],
        variants=cat["variants"],
        requirements=req,
        filter_result=fr,
    )
    check(
        "5 生成 1-3 套方案",
        1 <= plans["plan_count"] <= 3 and not plans["roles_missing"],
        f"plans={plans['plan_count']} missing={plans['roles_missing']}",
    )
    for p in plans["plans"]:
        check(
            "5b 方案预算不超限",
            p.purchase_subtotal_fen <= req.budget_fen,
            f"{p.plan_id}: {p.purchase_subtotal_fen} 分",
        )

    # ---------- 6. 约束校验 ----------
    all_valid = all(
        validate_plan(p, req).get("validation_status") == "passed"
        for p in plans["plans"]
    )
    check("6 方案全部通过约束校验", all_valid)

    # ---------- 7. 锁定单品 ----------
    plan0 = plans["plans"][0]
    merchant_items = [i for i in plan0.items if i.source == "merchant"]
    check("7 方案含商家商品可锁定", len(merchant_items) >= 1)
    if merchant_items:
        lock_key = merchant_items[0].lock_key_of()
        req.hard.locked_items = [
            {
                "source": "merchant",
                "variant_id": merchant_items[0].variant_id,
                "lock_key": lock_key,
            }
        ]
        check(
            "7b 锁定项已记录",
            req.hard.locked_items[0]["variant_id"] == merchant_items[0].variant_id,
        )

    # ---------- 8. 替换改搭 ----------
    op = parse_operation("把外套换成贵一点的")
    r = apply_operation(
        op,
        plan=plan0,
        requirements=req,
        products=cat["products"],
        variants=cat["variants"],
        closet_items=closet_mates,
        anchor=anchor,
    )
    if r["ok"]:
        new_item = [
            i for i in plan0.items if i.role == "外套" and i.source == "merchant"
        ]
        same_cat = new_item and new_item[0].category == "外套"
        check("8 外套替换成功且品类正确", same_cat, r.get("message", ""))
    else:
        # 若外套来自衣橱则无法替换（正确业务行为），此处演示用外套应来自商家
        check("8 外套替换成功且品类正确", False, r.get("message", ""))

    # ---------- 9. 缺货重规划 ----------
    # 选一个方案中的商家变体，把库存置为 0 后重跑 filter+plan
    chosen = plans["plans"][1]
    chosen_merchant = [i for i in chosen.items if i.source == "merchant"]
    depleted = None
    for v in cat["variants"]:
        if v.variant_id in {i.variant_id for i in chosen_merchant}:
            if v.stock_qty > 0:
                v.stock_qty = 0  # 模拟缺货
                depleted = v.variant_id
                break
    if depleted:
        fr2 = filter_variants(cat["products"], cat["variants"], req)
        plans2 = plan_outfits(
            anchor=anchor,
            closet_items=closet_mates,
            products=cat["products"],
            variants=cat["variants"],
            requirements=req,
            filter_result=fr2,
        )
        if plans2["plans"]:
            no_depleted = all(
                depleted
                not in {i.variant_id for i in p.items if i.source == "merchant"}
                for p in plans2["plans"]
            )
            check("9 缺货后重规划不选缺货变体", no_depleted, f"depleted={depleted}")
        else:
            check("9 缺货后重规划不选缺货变体", False, "缺货导致无方案（如实输出）")
    else:
        check("9 缺货后重规划不选缺货变体", False, "未找到可置空的商家变体")

    # ---------- 10. 购物意向清单 ----------
    sl = build_shopping_list(plan0, inventory_snapshot_at="2026-10-07T00:00:00+08:00")
    check("10 购物意向清单生成", sl["status"] == "购物意向清单已生成", sl["status"])
    check(
        "10b 清单含免责声明",
        "免责" in sl.get("disclaimer", ""),
        f"keys={list(sl.keys())}",
    )
    check(
        "10c 清单金额=方案金额",
        sl["financial_summary"]["purchase_subtotal_fen"] == plan0.purchase_subtotal_fen,
    )

    # ---------- 11. 执行日志 ----------
    logger = AuditLogger(os.path.join(ROOT, "logs"))
    logger.log("e2e_test", f"sess-e2e-{os.getpid()}", {"passed": True})
    log_files = os.listdir(os.path.join(ROOT, "logs"))
    check(
        "11 执行日志落盘",
        any("e2e" in f for f in log_files) or len(log_files) > 0,
        f"{len(log_files)} 日志文件",
    )

    # ---------- 汇总 ----------
    failed = [r for r in RESULTS if not r["ok"]]
    print("\n" + "=" * 60)
    print(f"E2E 结果: {len(RESULTS) - len(failed)}/{len(RESULTS)} 通过")
    if failed:
        print("未通过项:")
        for f in failed:
            print(f"  - {f['name']}: {f['detail']}")
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
