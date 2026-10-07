"""catalog_normalizer：商家商品表标准化与数据质量检查。

- 读取产品 CSV（utf-8-sig，兼容 BOM）。
- 商品级拒绝：sale_status 非 on_sale、重复 sku_id、缺少 category。
- 变体级拒绝：重复 variant_id、价格缺失(<0)、price_fen 非法。
- 汇总 normalized / rejected / warnings。
"""

from __future__ import annotations

import csv
import os

from .models import Product, Variant, empty_to_none, split_tags


def load_catalog(csv_path: str, variants_csv_path: str | None = None) -> dict:
    """读取并标准化商品表 + 变体表（变体表可单独指定；默认读取同目录 demo_variants.csv）。"""
    errors = []
    warnings = []
    seen_sku = set()
    seen_variant = set()
    products: list[Product] = []
    variants: list[Variant] = []

    # 1) 产品表
    if not os.path.exists(csv_path):
        return {
            "total": 0,
            "normalized": 0,
            "rejected": 0,
            "errors": [{"reason": "产品表文件不存在"}],
            "products": [],
            "variants": [],
        }

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    for i, r in enumerate(rows, start=2):  # 行号从2开始（表头为1）
        sku = (r.get("sku_id") or "").strip()
        if not sku:
            errors.append(
                {"row": i, "sku_id": sku, "reason": "缺少 sku_id", "action": "rejected"}
            )
            continue
        if sku in seen_sku:
            errors.append(
                {"row": i, "sku_id": sku, "reason": "重复 SKU", "action": "rejected"}
            )
            continue
        seen_sku.add(sku)

        status = r.get("sale_status") or ""
        if status not in ("on_sale", "off_shelf", "discontinued"):
            warnings.append(
                {
                    "row": i,
                    "sku_id": sku,
                    "reason": f"未知销售状态 {status!r}",
                    "action": "flagged",
                }
            )

        p = Product(
            product_id=(r.get("product_id") or "").strip(),
            merchant_id=(r.get("merchant_id") or "").strip(),
            sku_id=sku,
            product_name=(r.get("product_name") or "").strip(),
            category=(r.get("category") or "").strip(),
            color_tags=split_tags(r.get("color_tags")),
            material=empty_to_none(r.get("material")),
            pattern=empty_to_none(r.get("pattern")),
            silhouette=empty_to_none(r.get("silhouette")),
            style_tags=split_tags(r.get("style_tags")),
            season_tags=split_tags(r.get("season_tags")),
            scene_tags=split_tags(r.get("scene_tags")),
            image_ref=empty_to_none(r.get("image_ref")),
            product_url=empty_to_none(r.get("product_url")),
            sale_status=status or "on_sale",
            data_type=(r.get("data_type") or "SYNTHETIC_DEMO").strip(),
            rights_status=(r.get("rights_status") or "").strip(),
            updated_at=(r.get("updated_at") or "").strip(),
            is_sponsor=int(r.get("is_sponsor") or 0) == 1,
        )
        products.append(p)

    # 2) 变体表
    variants_path = variants_csv_path
    if variants_path is None:
        default_variants = os.path.join(os.path.dirname(csv_path), "demo_variants.csv")
        if os.path.exists(default_variants):
            variants_path = default_variants

    if variants_path is None or not os.path.exists(variants_path):
        warnings.append({"reason": "未找到变体表，variants 为空", "action": "flagged"})
    else:
        with open(variants_path, encoding="utf-8-sig", newline="") as f:
            vrows = list(csv.DictReader(f))
        for i, r in enumerate(vrows, start=2):
            vid = (r.get("variant_id") or "").strip()
            if not vid:
                continue
            if vid in seen_variant:
                errors.append(
                    {
                        "row": i,
                        "sku_id": r.get("sku_id"),
                        "variant_id": vid,
                        "reason": "重复变体编号",
                        "action": "rejected",
                    }
                )
                continue
            seen_variant.add(vid)

            price = _to_int(r.get("price_fen"), MISSING=-1)
            stock = _to_int(r.get("stock_qty"), MISSING=0)
            fee = _to_int(r.get("shipping_fee_fen"), MISSING=-1)
            if price < 0:
                errors.append(
                    {
                        "row": i,
                        "sku_id": r.get("sku_id"),
                        "variant_id": vid,
                        "reason": "价格缺失或非法",
                        "action": "rejected",
                    }
                )
                continue
            if stock < 0:
                errors.append(
                    {
                        "row": i,
                        "sku_id": r.get("sku_id"),
                        "variant_id": vid,
                        "reason": "库存为负",
                        "action": "rejected",
                    }
                )
                continue

            variants.append(
                Variant(
                    variant_id=vid,
                    product_id=(r.get("product_id") or "").strip(),
                    size_label=(r.get("size_label") or "").strip(),
                    color_label=empty_to_none(r.get("color_label")),
                    price_fen=price,
                    stock_qty=stock,
                    shipping_fee_fen=fee,
                    inventory_status=(r.get("inventory_status") or "unknown").strip(),
                    inventory_updated_at=(r.get("inventory_updated_at") or "").strip(),
                )
            )

    rejected = len(errors)
    return {
        "total": len(rows),
        "normalized": len(products),
        "variants_normalized": len(variants),
        "rejected": rejected,
        "errors": errors,
        "warnings": warnings,
        "products": products,
        "variants": variants,
    }


def load_demo(base_dir: str | None = None) -> dict:
    """便捷入口：加载演示目录下的商品与变体表。base_dir 为 data/inputs/raw。"""
    import os as _os

    if base_dir is None:
        here = _os.path.dirname(_os.path.abspath(__file__))
        base_dir = _os.path.abspath(
            _os.path.join(here, "..", "..", "data", "inputs", "raw")
        )
    return load_catalog(
        _os.path.join(base_dir, "demo_products.csv"),
        _os.path.join(base_dir, "demo_variants.csv"),
    )


def _to_int(v, MISSING: int = -1) -> int:
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return MISSING
