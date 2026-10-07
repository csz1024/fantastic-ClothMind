"""shopping_list_builder：购物意向清单生成。

规则：
- 自有衣物不计入购买金额，但也标注为"已有"而非免费商品。
- 预算结论必须区分：商品小计、已知费用、未知费用；
  存在未知费用时写"当前商品小计符合预算，最终支付金额仍需确认运费"，
  禁止写"总价保证不超过预算"。
- 无支付接口，最终状态只能为「购物意向清单已生成」。
- 商品只有在有真实链接时才显示"前往商品页"。
"""

from __future__ import annotations

from .models import Plan, gen_id, UNKNOWN_FEE


def build_shopping_list(
    plan: Plan, *, inventory_snapshot_at: str = "", merchant_name: str = "演示商家"
) -> dict:
    closet_items = []
    purchase_items = []
    known_fee_fen = 0
    unknown_fees: list[str] = []

    for i in plan.items:
        if i.source == "closet":
            closet_items.append(
                {
                    "item_id": i.ref_id,
                    "name": i.product_name or "自有衣物",
                    "role": i.role,
                    "image_ref": i.image_ref or "",
                }
            )
            continue

        p = {
            "sku_id": i.sku_id,
            "variant_id": i.variant_id,
            "name": i.product_name,
            "role": i.role,
            "size": i.size,
            "color": i.color,
            "price_fen": i.price_fen,
            "quantity": 1,
            "subtotal_fen": i.price_fen,
            "image_ref": i.image_ref or "",
            "product_url": i.product_url or "",
            "has_url": bool(i.product_url),
            "is_sponsor": i.is_sponsor,
        }
        purchase_items.append(p)
        if i.shipping_fee_fen >= 0:
            known_fee_fen += i.shipping_fee_fen
        else:
            unknown_fees.append(f"{i.sku_id}（{i.product_name}）")

    subtotal = plan.purchase_subtotal_fen
    if unknown_fees:
        message = "当前商品小计符合预算，最终支付金额仍需确认运费。"
        final_determined = False
        final_amount = None
    else:
        message = (
            "商品小计与已知费用合计为"
            + _yuan(subtotal + known_fee_fen)
            + "元，运费以商家结算为准。"
        )
        final_determined = True
        final_amount = subtotal + known_fee_fen

    pending = []
    if unknown_fees:
        pending.append(f"运费未知：{'、'.join(unknown_fees)}（{len(unknown_fees)}件）")
    pending.append("尺码合身度仅供参考，建议对照尺码表；商品图片与实物可能存在色差。")

    return {
        "list_id": gen_id("list"),
        "status": "购物意向清单已生成",
        "created_for_merchant": merchant_name,
        "closet_items": closet_items,
        "purchase_items": purchase_items,
        "financial_summary": {
            "purchase_subtotal_fen": subtotal,
            "known_fee_fen": known_fee_fen,
            "unknown_fee_list": unknown_fees,
            "final_amount_determined": final_determined,
            "final_amount_fen": final_amount,
            "message": message,
        },
        "inventory_snapshot_at": inventory_snapshot_at,
        "pending_confirmations": pending,
        "disclaimer": "免责声明：本清单仅为购物意向，不构成下单或购买承诺。价格、库存、运费以购买前页面复核为准。",
    }


def _yuan(fen: int) -> str:
    return f"{fen / 100:.2f}"
