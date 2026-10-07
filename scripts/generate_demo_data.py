# -*- coding: utf-8 -*-
"""生成30条SYNTHETIC_DEMO演示商品数据，含边界状态。"""

import csv
import os
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "inputs", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

NOW = datetime.now().isoformat()
OLD_TIME = (datetime.now() - timedelta(days=30)).isoformat()

products = []
variants = []


# 商品数据生成器
def add_product(
    pid,
    sku,
    name,
    cat,
    colors,
    material,
    pattern,
    silhouette,
    styles,
    seasons,
    scenes,
    sale_status,
    data_type,
    rights,
    url="",
    sponsor=False,
):
    products.append(
        {
            "product_id": pid,
            "merchant_id": "DEMO-MERCHANT-001",
            "sku_id": sku,
            "product_name": name + (" [赞助]" if sponsor else ""),
            "category": cat,
            "color_tags": ";".join(colors),
            "material": material,
            "pattern": pattern,
            "silhouette": silhouette,
            "style_tags": ";".join(styles),
            "season_tags": ";".join(seasons),
            "scene_tags": ";".join(scenes),
            "image_ref": f"demo://{sku}.png",
            "product_url": url,
            "sale_status": sale_status,
            "data_type": data_type,
            "rights_status": rights,
            "updated_at": NOW,
            "is_sponsor": "1" if sponsor else "0",
        }
    )


def add_variant(
    vid, pid, size, color, price_fen, stock, shipping_fen, status, updated_at
):
    variants.append(
        {
            "variant_id": vid,
            "product_id": pid,
            "size_label": size,
            "color_label": color,
            "price_fen": price_fen,
            "stock_qty": stock,
            "shipping_fee_fen": shipping_fen,
            "inventory_status": status,
            "inventory_updated_at": updated_at,
        }
    )


# ===== 上衣（6件）=====
# 1. 基础白T - 正常
add_product(
    "P001",
    "OW-TOP-001",
    "基础纯棉白T恤",
    "上衣",
    ["白色"],
    "棉",
    "纯色",
    "宽松",
    ["休闲"],
    ["春", "夏"],
    ["上课", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-TOP-001",
)
add_variant("V001", "P001", "M", "白色", 5900, 50, 0, "in_stock", NOW)
add_variant("V002", "P001", "L", "白色", 5900, 30, 0, "in_stock", NOW)

# 2. 条纹衬衫 - 正常
add_product(
    "P002",
    "OW-TOP-002",
    "蓝白条纹衬衫",
    "上衣",
    ["蓝色", "白色"],
    "棉混纺",
    "条纹",
    "直筒",
    ["正式", "休闲"],
    ["春", "秋"],
    ["面试", "答辩", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-TOP-002",
)
add_variant("V003", "P002", "M", "蓝白", 12900, 20, 0, "in_stock", NOW)
add_variant("V004", "P002", "L", "蓝白", 12900, 15, 0, "in_stock", NOW)

# 3. 黑色高领 - M码缺货（边界1）
add_product(
    "P003",
    "OW-TOP-003",
    "黑色高领打底衫",
    "上衣",
    ["黑色"],
    "腈纶混纺",
    "纯色",
    "修身",
    ["正式"],
    ["秋", "冬"],
    ["面试", "答辩"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-TOP-003",
)
add_variant("V005", "P003", "S", "黑色", 8900, 10, 0, "in_stock", NOW)
add_variant("V006", "P003", "M", "黑色", 8900, 0, 0, "out_of_stock", NOW)  # M缺货
add_variant("V007", "P003", "L", "黑色", 8900, 8, 0, "in_stock", NOW)

# 4. 印花卫衣 - 价格缺失（边界2）
add_product(
    "P004",
    "OW-TOP-004",
    "复古印花卫衣",
    "上衣",
    ["米色", "棕色"],
    "棉",
    "印花",
    "宽松",
    ["复古", "休闲"],
    ["秋", "冬"],
    ["社团活动", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-TOP-004",
)
add_variant("V008", "P004", "M", "米色", -1, 25, 0, "in_stock", NOW)  # 价格缺失
add_variant("V009", "P004", "L", "米色", -1, 20, 0, "in_stock", NOW)

# 5. 灰色西装外套（误分类为上衣，实际应为外套）- 库存为零（边界3）
add_product(
    "P005",
    "OW-TOP-005",
    "浅灰休闲西装",
    "外套",
    ["灰色"],
    "聚酯纤维",
    "纯色",
    "修身",
    ["正式"],
    ["春", "秋"],
    ["面试", "答辩"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
)
add_variant("V010", "P005", "M", "灰色", 19900, 0, 0, "out_of_stock", NOW)  # 库存为零
add_variant("V011", "P005", "L", "灰色", 19900, 0, 0, "out_of_stock", NOW)

# 6.  OversizeT恤 - 赞助商品（边界10）
add_product(
    "P006",
    "OW-TOP-006",
    "联名款OversizeT恤",
    "上衣",
    ["黑色"],
    "棉",
    "印花",
    "Oversize",
    ["潮流", "休闲"],
    ["夏"],
    ["社团活动"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    sponsor=True,
)
add_variant("V012", "P006", "M", "黑色", 29900, 100, 0, "in_stock", NOW)
add_variant("V013", "P006", "L", "黑色", 29900, 80, 0, "in_stock", NOW)

# ===== 下装（6件）=====
# 7. 深蓝牛仔裤 - 正常
add_product(
    "P007",
    "OW-BTM-001",
    "深蓝直筒牛仔裤",
    "下装",
    ["蓝色"],
    "棉",
    "纯色",
    "直筒",
    ["休闲", "正式"],
    ["春", "夏", "秋"],
    ["上课", "面试", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-BTM-001",
)
add_variant("V014", "P007", "M", "蓝色", 15900, 40, 0, "in_stock", NOW)
add_variant("V015", "P007", "L", "蓝色", 15900, 35, 0, "in_stock", NOW)

# 8. 黑色西裤 - 正常
add_product(
    "P008",
    "OW-BTM-002",
    "黑色修身西裤",
    "下装",
    ["黑色"],
    "聚酯纤维",
    "纯色",
    "修身",
    ["正式"],
    ["春", "秋", "冬"],
    ["面试", "答辩"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-BTM-002",
)
add_variant("V016", "P008", "M", "黑色", 13900, 25, 0, "in_stock", NOW)
add_variant("V017", "P008", "L", "黑色", 13900, 20, 0, "in_stock", NOW)

# 9. 卡其工装裤 - 下架（边界4）
add_product(
    "P009",
    "OW-BTM-003",
    "卡其工装裤",
    "下装",
    ["卡其色"],
    "棉",
    "纯色",
    "宽松",
    ["休闲"],
    ["春", "夏", "秋"],
    ["社团活动", "日常通勤"],
    "off_shelf",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-BTM-003",
)
add_variant("V018", "P009", "M", "卡其", 11900, 5, 0, "low_stock", OLD_TIME)

# 10. 灰色运动裤 - 运费未知（边界5）
add_product(
    "P010",
    "OW-BTM-004",
    "灰色束脚运动裤",
    "下装",
    ["灰色"],
    "聚酯纤维",
    "纯色",
    "宽松",
    ["运动", "休闲"],
    ["春", "秋", "冬"],
    ["上课", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-BTM-004",
)
add_variant("V019", "P010", "M", "灰色", 9900, 60, -1, "in_stock", NOW)  # 运费未知
add_variant("V020", "P010", "L", "灰色", 9900, 55, -1, "in_stock", NOW)

# 11. 百褶裙 - 没有购买链接（边界6）
add_product(
    "P011",
    "OW-BTM-005",
    "黑色百褶裙",
    "下装",
    ["黑色"],
    "聚酯纤维",
    "纯色",
    "A字",
    ["正式", "休闲"],
    ["春", "夏", "秋"],
    ["面试", "社团活动"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "",
)  # 无链接
add_variant("V021", "P011", "M", "黑色", 10900, 18, 0, "in_stock", NOW)

# 12. 白色阔腿裤 - 库存更新时间较旧（边界7）
add_product(
    "P012",
    "OW-BTM-006",
    "白色高腰阔腿裤",
    "下装",
    ["白色"],
    "聚酯纤维",
    "纯色",
    "宽松",
    ["休闲", "正式"],
    ["春", "夏"],
    ["上课", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-BTM-006",
)
add_variant("V022", "P012", "M", "白色", 12900, 12, 0, "in_stock", OLD_TIME)  # 旧时间
add_variant("V023", "P012", "L", "白色", 12900, 10, 0, "in_stock", OLD_TIME)

# ===== 外套（6件）=====
# 13. 卡其风衣 - 正常
add_product(
    "P013",
    "OW-OUT-001",
    "卡其色中长款风衣",
    "外套",
    ["卡其色"],
    "棉",
    "纯色",
    "直筒",
    ["正式", "休闲"],
    ["春", "秋"],
    ["面试", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-OUT-001",
)
add_variant("V024", "P013", "M", "卡其", 25900, 15, 0, "in_stock", NOW)
add_variant("V025", "P013", "L", "卡其", 25900, 12, 0, "in_stock", NOW)

# 14. 黑色羽绒服 - 只有一个尺码（边界8）
add_product(
    "P014",
    "OW-OUT-002",
    "黑色轻薄羽绒服",
    "外套",
    ["黑色"],
    "聚酯纤维",
    "纯色",
    "修身",
    ["正式", "休闲"],
    ["冬"],
    ["上课", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-OUT-002",
)
add_variant("V026", "P014", "均码", "黑色", 32900, 8, 800, "in_stock", NOW)  # 仅均码

# 15. 牛仔夹克 - 正常
add_product(
    "P015",
    "OW-OUT-003",
    "复古水洗牛仔夹克",
    "外套",
    ["蓝色"],
    "棉",
    "纯色",
    "宽松",
    ["复古", "休闲"],
    ["春", "秋"],
    ["社团活动", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-OUT-003",
)
add_variant("V027", "P015", "M", "蓝色", 18900, 22, 0, "in_stock", NOW)
add_variant("V028", "P015", "L", "蓝色", 18900, 18, 0, "in_stock", NOW)

# 16. 灰色毛呢大衣 - 超预算商品（边界9，>500元）
add_product(
    "P016",
    "OW-OUT-004",
    "灰色羊毛混纺大衣",
    "外套",
    ["灰色"],
    "羊毛混纺",
    "纯色",
    "直筒",
    ["正式"],
    ["冬"],
    ["面试", "答辩"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-OUT-004",
)
add_variant("V029", "P016", "M", "灰色", 59900, 5, 0, "in_stock", NOW)  # 599元超预算
add_variant("V030", "P016", "L", "灰色", 59900, 3, 0, "in_stock", NOW)

# 17. 运动风外套 - 正常
add_product(
    "P017",
    "OW-OUT-005",
    "白色运动风衣",
    "外套",
    ["白色"],
    "聚酯纤维",
    "纯色",
    "宽松",
    ["运动", "休闲"],
    ["春", "秋"],
    ["上课", "社团活动"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-OUT-005",
)
add_variant("V031", "P017", "M", "白色", 14900, 30, 0, "in_stock", NOW)
add_variant("V032", "P017", "L", "白色", 14900, 25, 0, "in_stock", NOW)

# 18. 棕色皮夹克 - 下架
add_product(
    "P018",
    "OW-OUT-006",
    "棕色仿皮夹克",
    "外套",
    ["棕色"],
    "PU",
    "纯色",
    "修身",
    ["复古", "休闲"],
    ["秋", "冬"],
    ["社团活动"],
    "discontinued",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
)
add_variant("V033", "P018", "M", "棕色", 22900, 0, 0, "out_of_stock", OLD_TIME)

# ===== 鞋类（6件）=====
# 19. 白色板鞋 - 正常
add_product(
    "P019",
    "OW-SHO-001",
    "经典白色板鞋",
    "鞋类",
    ["白色"],
    "帆布",
    "纯色",
    "标准",
    ["休闲"],
    ["春", "夏", "秋"],
    ["上课", "日常通勤", "社团活动"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-SHO-001",
)
add_variant("V034", "P019", "39", "白色", 19900, 45, 0, "in_stock", NOW)
add_variant("V035", "P019", "40", "白色", 19900, 40, 0, "in_stock", NOW)
add_variant("V036", "P019", "41", "白色", 19900, 35, 0, "in_stock", NOW)

# 20. 黑色皮鞋 - 正常
add_product(
    "P020",
    "OW-SHO-002",
    "黑色商务皮鞋",
    "鞋类",
    ["黑色"],
    "人造革",
    "纯色",
    "标准",
    ["正式"],
    ["春", "夏", "秋", "冬"],
    ["面试", "答辩"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-SHO-002",
)
add_variant("V037", "P020", "39", "黑色", 24900, 20, 0, "in_stock", NOW)
add_variant("V038", "P020", "40", "黑色", 24900, 18, 0, "in_stock", NOW)
add_variant("V039", "P020", "41", "黑色", 24900, 15, 0, "in_stock", NOW)

# 21. 棕色乐福鞋 - 39码缺货
add_product(
    "P021",
    "OW-SHO-003",
    "棕色乐福鞋",
    "鞋类",
    ["棕色"],
    "人造革",
    "纯色",
    "标准",
    ["正式", "休闲"],
    ["春", "夏", "秋"],
    ["面试", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-SHO-003",
)
add_variant("V040", "P021", "39", "棕色", 17900, 0, 0, "out_of_stock", NOW)  # 39缺货
add_variant("V041", "P021", "40", "棕色", 17900, 12, 0, "in_stock", NOW)
add_variant("V042", "P021", "41", "棕色", 17900, 10, 0, "in_stock", NOW)

# 22. 运动鞋 - 运费未知
add_product(
    "P022",
    "OW-SHO-004",
    "灰白拼色运动鞋",
    "鞋类",
    ["灰色", "白色"],
    "网面",
    "拼色",
    "标准",
    ["运动", "休闲"],
    ["春", "夏", "秋"],
    ["上课", "社团活动"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-SHO-004",
)
add_variant("V043", "P022", "39", "灰白", 22900, 25, -1, "in_stock", NOW)  # 运费未知
add_variant("V044", "P022", "40", "灰白", 22900, 20, -1, "in_stock", NOW)
add_variant("V045", "P022", "41", "灰白", 22900, 18, -1, "in_stock", NOW)

# 23. 马丁靴 - 库存为零
add_product(
    "P023",
    "OW-SHO-005",
    "黑色马丁靴",
    "鞋类",
    ["黑色"],
    "PU",
    "纯色",
    "标准",
    ["复古", "休闲"],
    ["秋", "冬"],
    ["社团活动", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
)
add_variant("V046", "P023", "39", "黑色", 26900, 0, 0, "out_of_stock", NOW)
add_variant("V047", "P023", "40", "黑色", 26900, 0, 0, "out_of_stock", NOW)
add_variant("V048", "P023", "41", "黑色", 26900, 0, 0, "out_of_stock", NOW)

# 24. 帆布鞋 - 价格缺失
add_product(
    "P024",
    "OW-SHO-006",
    "复古帆布鞋",
    "鞋类",
    ["米色"],
    "帆布",
    "纯色",
    "标准",
    ["休闲", "复古"],
    ["春", "夏"],
    ["上课", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-SHO-006",
)
add_variant("V049", "P024", "39", "米色", -1, 30, 0, "in_stock", NOW)  # 价格缺失
add_variant("V050", "P024", "40", "米色", -1, 28, 0, "in_stock", NOW)
add_variant("V051", "P024", "41", "米色", -1, 25, 0, "in_stock", NOW)

# ===== 包饰（6件）=====
# 25. 黑色单肩包 - 正常
add_product(
    "P025",
    "OW-ACC-001",
    "黑色简约单肩包",
    "包饰",
    ["黑色"],
    "PU",
    "纯色",
    "标准",
    ["正式", "休闲"],
    ["春", "夏", "秋", "冬"],
    ["上课", "面试", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-ACC-001",
)
add_variant("V052", "P025", "均码", "黑色", 15900, 30, 0, "in_stock", NOW)

# 26. 棕色双肩包 - 正常
add_product(
    "P026",
    "OW-ACC-002",
    "棕色帆布双肩包",
    "包饰",
    ["棕色"],
    "帆布",
    "纯色",
    "标准",
    ["休闲"],
    ["春", "夏", "秋", "冬"],
    ["上课", "社团活动"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-ACC-002",
)
add_variant("V053", "P026", "均码", "棕色", 12900, 40, 0, "in_stock", NOW)

# 27. 米色帆布包 - 下架
add_product(
    "P027",
    "OW-ACC-003",
    "米色托特帆布包",
    "包饰",
    ["米色"],
    "帆布",
    "纯色",
    "标准",
    ["休闲"],
    ["春", "夏", "秋"],
    ["上课", "日常通勤"],
    "off_shelf",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
)
add_variant("V054", "P027", "均码", "米色", 8900, 0, 0, "out_of_stock", OLD_TIME)

# 28. 银色项链 - 只有一个尺码/无尺码概念
add_product(
    "P028",
    "OW-ACC-004",
    "银色链条项链",
    "包饰",
    ["银色"],
    "合金",
    "纯色",
    "标准",
    ["潮流", "正式"],
    ["春", "夏", "秋", "冬"],
    ["社团活动", "面试"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-ACC-004",
)
add_variant("V055", "P028", "均码", "银色", 6900, 50, 0, "in_stock", NOW)

# 29. 黑色皮带 - 价格缺失
add_product(
    "P029",
    "OW-ACC-005",
    "黑色简约皮带",
    "包饰",
    ["黑色"],
    "PU",
    "纯色",
    "标准",
    ["正式", "休闲"],
    ["春", "夏", "秋", "冬"],
    ["面试", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-ACC-005",
)
add_variant("V056", "P029", "均码", "黑色", -1, 20, 0, "in_stock", NOW)  # 价格缺失

# 30. 灰色围巾 - 库存更新时间较旧
add_product(
    "P030",
    "OW-ACC-006",
    "灰色羊毛围巾",
    "包饰",
    ["灰色"],
    "羊毛混纺",
    "纯色",
    "标准",
    ["正式", "休闲"],
    ["冬"],
    ["面试", "日常通勤"],
    "on_sale",
    "SYNTHETIC_DEMO",
    "demo_placeholder",
    "https://demo.example.com/OW-ACC-006",
)
add_variant("V057", "P030", "均码", "灰色", 9900, 15, 0, "in_stock", OLD_TIME)  # 旧时间

# 写入 products.csv
prod_path = os.path.join(RAW_DIR, "demo_products.csv")
with open(prod_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "product_id",
            "merchant_id",
            "sku_id",
            "product_name",
            "category",
            "color_tags",
            "material",
            "pattern",
            "silhouette",
            "style_tags",
            "season_tags",
            "scene_tags",
            "image_ref",
            "product_url",
            "sale_status",
            "data_type",
            "rights_status",
            "updated_at",
            "is_sponsor",
        ],
    )
    writer.writeheader()
    writer.writerows(products)
print(f"saved: {prod_path} ({len(products)} products)")

# 写入 product_variants.csv
var_path = os.path.join(RAW_DIR, "demo_variants.csv")
with open(var_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "variant_id",
            "product_id",
            "size_label",
            "color_label",
            "price_fen",
            "stock_qty",
            "shipping_fee_fen",
            "inventory_status",
            "inventory_updated_at",
        ],
    )
    writer.writeheader()
    writer.writerows(variants)
print(f"saved: {var_path} ({len(variants)} variants)")

# 验证边界状态
print("\n边界状态检查:")
print(f"- M码缺货: P003(OW-TOP-003) 黑色高领打底衫 M stock=0")
print(
    f"- 价格缺失: P004(OW-TOP-004) price=-1, P024(OW-SHO-006) price=-1, P029(OW-ACC-005) price=-1"
)
print(f"- 库存为零: P005(OW-TOP-005) stock=0, P023(OW-SHO-005) stock=0")
print(
    f"- 下架: P009(OW-BTM-003) off_shelf, P018(OW-OUT-006) discontinued, P027(OW-ACC-003) off_shelf"
)
print(f"- 运费未知: P010(OW-BTM-004) shipping=-1, P022(OW-SHO-004) shipping=-1")
print(f"- 无购买链接: P011(OW-BTM-005) url=''")
print(f"- 旧库存时间: P012, P018, P027, P030 updated_at={OLD_TIME[:10]}")
print(f"- 单尺码: P014(OW-OUT-002) 仅均码, P025-P030 包饰均码")
print(f"- 超预算: P016(OW-OUT-004) 599元 > 500元")
print(f"- 赞助商品: P006(OW-TOP-006) [赞助]")
print(f"\n总计: {len(products)} products, {len(variants)} variants")
