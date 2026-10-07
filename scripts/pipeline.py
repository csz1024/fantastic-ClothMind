"""
pipeline.py — OutfitWindow 主工作流管道（命令行可复现）。

完整链路（对齐 SKILL.md）：
  1. 隐私检查      -> input_privacy_audit
  2. 衣物识别卡    -> garment_card_builder
  3. 需求解析      -> requirement_parser
  4. 商品目录加载   -> catalog_normalizer
  5. 硬约束过滤     -> hard_constraint_filter
  6. 搭配组合规划   -> outfit_planner
  7. 约束校验      -> constraint_validator
  8. 橱窗展示      -> window_board_builder
  9. 交互改搭      -> interactive_replanner
 10. 购物意向清单   -> shopping_list_builder
 11. 执行日志      -> audit_logger

运行：
  cd outfitwindow
  python scripts/pipeline.py --item-category 上衣 --item-color 白色 \
       --budget-yuan 500 --size-top M --size-bottom L --size-shoe 40 \
       --output-dir data/outputs

演示模式（无真实图片）：
  python scripts/pipeline.py --demo --output-dir data/outputs
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

# 添加 skills_lib 到路径
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from skills_lib import (
    audit_image,
    build_garment_card,
    parse_requirement,
    load_catalog,
    filter_variants,
    plan_outfits,
    validate_all,
    parse_operation,
    apply_operation,
    build_board,
    build_shopping_list,
    AuditLogger,
    ClosetItem,
    Requirements,
    HardConstraints,
)


class PipelineRunner:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = AuditLogger(os.path.join(output_dir, "..", "..", "logs"))
        self.session_id = f"sess-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self.results: dict = {}

    def log(self, event_type: str, operation: dict):
        return self.logger.log(event_type, self.session_id, operation)

    def run(self, *, item_args: dict, req_args: dict, demo_mode: bool = False) -> dict:
        t0 = time.time()
        print("=" * 60)
        print("OutfitWindow Pipeline")
        print(f"session_id: {self.session_id}")
        print(f"demo_mode: {demo_mode}")
        print("=" * 60)

        # 1) 隐私检查
        print("\n[1/11] 隐私检查")
        privacy = audit_image(
            item_args.get("image_path", ""),
            mode="demo" if demo_mode else "manual",
            user_confirmed=True,
        )
        print(f"  -> passed={privacy['passed']}, mode={privacy['mode']}")
        self.log(
            "privacy_check", {"passed": privacy["passed"], "mode": privacy["mode"]}
        )
        if not privacy["passed"]:
            return self._fail("隐私检查未通过", {"step": 1})

        # 2) 衣物识别卡
        print("\n[2/11] 衣物识别卡")
        if demo_mode:
            card = build_garment_card("", source="demo", demo_item=self._demo_anchor())
        else:
            card = build_garment_card(
                item_args.get("image_path", ""),
                source="user_input",
                user_input={
                    "category": item_args["category"],
                    "primary_color": item_args["color"],
                    "pattern": item_args.get("pattern"),
                    "silhouette": item_args.get("silhouette"),
                    "style_tags": item_args.get("style_tags", []),
                    "season_tags": item_args.get("season_tags", []),
                    "material_guess": item_args.get("material", "unknown"),
                },
            )
        if not card.get("valid"):
            return self._fail(f"衣物识别失败: {card.get('error')}", {"step": 2})
        print(
            f"  -> category={card['category']}, color={card['primary_color']}, needs_confirmation={card.get('needs_user_confirmation')}"
        )
        self.log(
            "garment_card",
            {"item_id": card.get("item_id"), "category": card["category"]},
        )

        # 3) 需求解析
        print("\n[3/11] 需求解析")
        req_result = parse_requirement(
            occasion=req_args.get("occasion", ""),
            budget_yuan=req_args.get("budget_yuan", 0),
            size_requirements={
                "上衣": req_args.get("size_top", ""),
                "下装": req_args.get("size_bottom", ""),
                "外套": req_args.get("size_out", ""),
                "鞋类": req_args.get("size_shoe", ""),
            },
            exclude_colors=req_args.get("exclude_colors", []),
            exclude_silhouettes=req_args.get("exclude_silhouettes", []),
        )
        req: Requirements = req_result["requirements"]
        if req_result["conflicts"]:
            print(f"  -> conflicts: {req_result['conflicts']}")
        print(
            f"  -> budget_fen={req.budget_fen}, occasion={req.occasion}, sizes={req.size_requirements}"
        )
        self.log(
            "requirement_parsed",
            {"budget_fen": req.budget_fen, "occasion": req.occasion},
        )

        # 4) 商品目录加载
        print("\n[4/11] 商品目录加载")
        catalog = load_catalog(
            os.path.join(HERE, "..", "data", "inputs", "raw", "demo_products.csv"),
            os.path.join(HERE, "..", "data", "inputs", "raw", "demo_variants.csv"),
        )
        print(
            f"  -> products={catalog['normalized']}, variants={catalog['variants_normalized']}, rejected={catalog['rejected']}"
        )
        self.log(
            "catalog_loaded",
            {
                "products": catalog["normalized"],
                "variants": catalog["variants_normalized"],
                "rejected": catalog["rejected"],
            },
        )

        # 5) 硬约束过滤
        print("\n[5/11] 硬约束过滤")
        fr = filter_variants(catalog["products"], catalog["variants"], req)
        print(f"  -> passed={fr['passed_count']}, failed={fr['failed_count']}")
        self.log(
            "filter_done", {"passed": fr["passed_count"], "failed": fr["failed_count"]}
        )
        if not fr["passed"]:
            return self._fail(
                "没有商品通过硬约束过滤（请放宽预算/尺码/排除项）", {"step": 5}
            )

        # 6) 搭配组合规划
        print("\n[6/11] 搭配组合规划")
        anchor = (
            self._demo_anchor()
            if demo_mode
            else self._build_anchor_from_card(card, item_args)
        )
        # 衣橱伙伴（演示数据）
        closet_mates = self._demo_closet_mates() if demo_mode else []
        plan_result = plan_outfits(
            anchor=anchor,
            closet_items=closet_mates,
            products=catalog["products"],
            variants=catalog["variants"],
            requirements=req,
            filter_result=fr,
        )
        print(
            f"  -> plans={plan_result['plan_count']}, filled_roles={plan_result['roles_filled']}, missing={plan_result['roles_missing']}"
        )
        self.log("plans_generated", {"plan_count": plan_result["plan_count"]})
        if not plan_result["plans"]:
            return self._fail("未能生成任何搭配方案", {"step": 6})

        # 7) 约束校验
        print("\n[7/11] 约束校验")
        val_results = validate_all(plan_result["plans"], req)
        for v in val_results:
            print(
                f"  -> {v['plan_id']} status={v['validation_status']} failed={v['failed_reasons']}"
            )
        self.log(
            "validation_done",
            {
                "results": [
                    {"plan_id": v["plan_id"], "status": v["validation_status"]}
                    for v in val_results
                ]
            },
        )

        # 8) 橱窗展示（降级为卡片）
        print("\n[8/11] 橱窗展示")
        boards = [build_board(p) for p in plan_result["plans"]]
        print(f"  -> boards={len(boards)} (degraded card_grid)")
        self.log("boards_built", {"board_count": len(boards), "mode": "degraded"})

        # 9) 交互改搭（演示：替换第一个方案的外套为更便宜的商家商品）
        print("\n[9/11] 交互改搭")
        if plan_result["plans"]:
            op = parse_operation("把外套换成便宜一点的")
            r = apply_operation(
                op,
                plan=plan_result["plans"][0],
                requirements=req,
                products=catalog["products"],
                variants=catalog["variants"],
                closet_items=closet_mates,
                anchor=anchor,
            )
            print(f"  -> replan ok={r['ok']}, msg={r.get('message')}")
            self.log(
                "replanner_applied", {"ok": r["ok"], "message": r.get("message", "")}
            )

        # 10) 购物意向清单
        print("\n[10/11] 购物意向清单")
        confirmed = plan_result["plans"][0]
        sl = build_shopping_list(
            confirmed, inventory_snapshot_at=datetime.now(timezone.utc).isoformat()
        )
        print(
            f"  -> status={sl['status']}, purchase_items={len(sl['purchase_items'])}, subtotal=¥{sl['financial_summary']['purchase_subtotal_fen'] / 100:.2f}"
        )
        self.log(
            "shopping_list_built",
            {"list_id": sl["list_id"], "items": len(sl["purchase_items"])},
        )

        # 11) 保存产物
        print("\n[11/11] 保存产物")
        outputs = {
            "plans": [p.to_dict() for p in plan_result["plans"]],
            "boards": boards,
            "shopping_list": sl,
            "filter_details": fr["details"][:20],  # 只保留前20条避免过大
            "requirements": req.to_dict(),
        }
        out_path = os.path.join(self.output_dir, "pipeline_result.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(outputs, f, ensure_ascii=False, indent=1)
        print(f"  -> saved: {out_path}")

        elapsed = round(time.time() - t0, 3)
        self.log(
            "pipeline_complete",
            {"elapsed_sec": elapsed, "plans": len(plan_result["plans"])},
        )
        print(f"\n✅ Pipeline complete in {elapsed}s")

        return {
            "ok": True,
            "plans": plan_result["plans"],
            "shopping_list": sl,
            "output_path": out_path,
            "elapsed": elapsed,
        }

    # -- helpers --
    def _fail(self, message: str, extra: dict) -> dict:
        self.log("pipeline_failed", {"message": message, **extra})
        print(f"\n❌ Pipeline failed: {message}")
        return {"ok": False, "message": message, **extra}

    def _demo_anchor(self):
        return ClosetItem(
            item_id="C001",
            user_id="u-demo",
            image_ref="",
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

    def _demo_closet_mates(self):
        return [
            ClosetItem(
                item_id="C002",
                user_id="u-demo",
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
                user_id="u-demo",
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

    def _build_anchor_from_card(self, card: dict, item_args: dict) -> ClosetItem:
        return ClosetItem(
            item_id=card.get("item_id", "C-web"),
            user_id="u-web",
            image_ref=item_args.get("image_path", ""),
            category=card["category"],
            primary_color=card["primary_color"],
            pattern=card.get("pattern"),
            silhouette=card.get("silhouette"),
            season_tags=card.get("season_tags", []),
            style_tags=card.get("style_tags", []),
            material_guess=card.get("material_guess", "unknown"),
            user_confirmed=True,
            available_status="available",
            source="user_input",
        )


def main():
    parser = argparse.ArgumentParser(description="OutfitWindow Pipeline")
    parser.add_argument("--output-dir", default="data/outputs", help="输出目录")
    parser.add_argument(
        "--demo", action="store_true", help="演示模式（使用预设衣物与需求）"
    )
    parser.add_argument("--item-category", default="上衣")
    parser.add_argument("--item-color", default="白色")
    parser.add_argument("--item-pattern", default="纯色")
    parser.add_argument("--item-silhouette", default="宽松")
    parser.add_argument("--budget-yuan", type=float, default=500)
    parser.add_argument("--size-top", default="M")
    parser.add_argument("--size-bottom", default="L")
    parser.add_argument("--size-out", default="M")
    parser.add_argument("--size-shoe", default="40")
    parser.add_argument("--occasion", default="上课与日常通勤")
    args = parser.parse_args()

    runner = PipelineRunner(args.output_dir)
    result = runner.run(
        item_args={
            "category": args.item_category,
            "color": args.item_color,
            "pattern": args.item_pattern,
            "silhouette": args.item_silhouette,
        },
        req_args={
            "occasion": args.occasion,
            "budget_yuan": args.budget_yuan,
            "size_top": args.size_top,
            "size_bottom": args.size_bottom,
            "size_out": args.size_out,
            "size_shoe": args.size_shoe,
        },
        demo_mode=args.demo,
    )
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
