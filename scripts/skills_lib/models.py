"""公共常量与基础数据结构。"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

# 类别枚举（需求与商品库共用）
CATEGORIES = ["上衣", "下装", "外套", "鞋类", "包饰"]

# 场景枚举
SCENES = ["上课与日常通勤", "面试与答辩", "社团活动与普通社交"]

# 销售状态
SALE_ON_SALE = "on_sale"
SALE_OFF_SHELF = "off_shelf"
SALE_DISCONTINUED = "discontinued"

# 缺省预算（分）与方案上限
DEFAULT_BUDGET_FEN = 50000
MAX_PLAN_ITEMS = 5
MAX_PLANS = 3

UNKNOWN_FEE = -1
MISSING_PRICE = -1


def empty_to_none(v):
    """空字符串 / 空白 -> None。"""
    if v is None:
        return None
    v = str(v).strip()
    return v if v else None


def split_tags(v):
    """分号分隔的标签列表。"""
    if not v:
        return []
    return [t.strip() for t in str(v).split(";") if t.strip()]


@dataclass
class Product:
    product_id: str
    merchant_id: str
    sku_id: str
    product_name: str
    category: str
    color_tags: list = field(default_factory=list)
    material: Optional[str] = None
    pattern: Optional[str] = None
    silhouette: Optional[str] = None
    style_tags: list = field(default_factory=list)
    season_tags: list = field(default_factory=list)
    scene_tags: list = field(default_factory=list)
    image_ref: Optional[str] = None
    product_url: Optional[str] = None
    sale_status: str = SALE_ON_SALE
    data_type: str = "SYNTHETIC_DEMO"
    rights_status: str = "demo_placeholder"
    updated_at: str = ""
    is_sponsor: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class Variant:
    variant_id: str
    product_id: str
    size_label: str
    color_label: Optional[str] = None
    price_fen: int = MISSING_PRICE
    stock_qty: int = 0
    shipping_fee_fen: int = 0
    inventory_status: str = "unknown"
    inventory_updated_at: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class ClosetItem:
    item_id: str
    user_id: str
    image_ref: str
    category: str
    primary_color: str
    secondary_colors: list = field(default_factory=list)
    pattern: Optional[str] = None
    silhouette: Optional[str] = None
    material_guess: Optional[str] = "unknown"
    season_tags: list = field(default_factory=list)
    style_tags: list = field(default_factory=list)
    user_confirmed: bool = True
    available_status: str = "available"
    created_at: str = ""
    updated_at: str = ""
    source: str = "user_input"  # user_input / demo / vision_service / closet

    def to_dict(self):
        return asdict(self)


@dataclass
class HardConstraints:
    exclude_colors: list = field(default_factory=list)
    exclude_silhouettes: list = field(default_factory=list)
    exclude_categories: list = field(default_factory=list)
    max_budget_fen: int = DEFAULT_BUDGET_FEN
    locked_items: list = field(
        default_factory=list
    )  # [{source, sku_id/variant_id/item_id}]

    def to_dict(self):
        return asdict(self)


@dataclass
class Requirements:
    occasion: str = ""
    temperature_text: str = ""
    budget_fen: int = DEFAULT_BUDGET_FEN
    size_requirements: dict = field(default_factory=dict)  # {category: size}
    hard: HardConstraints = field(default_factory=HardConstraints)
    soft_preferences: dict = field(default_factory=dict)
    missing_required: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        d["hard"] = self.hard.to_dict()
        return d


@dataclass
class PlanItem:
    source: str  # closet / merchant
    role: str
    ref_id: str  # closet item_id 或 merchant variant_id
    sku_id: Optional[str] = None
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    product_name: str = ""
    category: str = ""
    size: str = ""
    color: str = ""
    price_fen: int = 0
    image_ref: Optional[str] = None
    product_url: Optional[str] = None
    lock_key: Optional[str] = None
    is_sponsor: bool = False
    shipping_fee_fen: int = 0

    def lock_key_of(self) -> str:
        return self.lock_key or (
            f"merchant:{self.variant_id}"
            if self.source == "merchant"
            else f"closet:{self.ref_id}"
        )

    def to_dict(self):
        return asdict(self)


@dataclass
class Plan:
    plan_id: str
    plan_label: str
    items: list = field(default_factory=list)  # list[PlanItem]
    purchase_subtotal_fen: int = 0
    reasoning: str = ""
    validation: Optional[dict] = None

    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "plan_label": self.plan_label,
            "items": [i.to_dict() for i in self.items],
            "purchase_subtotal_fen": self.purchase_subtotal_fen,
            "reasoning": self.reasoning,
            "validation": self.validation,
        }


def gen_id(prefix: str, n: int = 12) -> str:
    """轻量伪随机 id（演示用，不依赖外部库）。"""
    import random
    import string

    chars = string.ascii_lowercase + string.digits
    return prefix + "-" + "".join(random.choice(chars) for _ in range(n))
