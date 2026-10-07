# -*- coding: utf-8 -*-
"""生成 OutfitWindow 7 张数据表的 JSON Schema。"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(ROOT, "data", "schema")
os.makedirs(SCHEMA_DIR, exist_ok=True)

schemas = {
    "closet_items": {
        "description": "用户已有衣物表",
        "fields": [
            {
                "name": "item_id",
                "type": "string",
                "required": True,
                "description": "衣物唯一标识",
            },
            {
                "name": "user_id",
                "type": "string",
                "required": True,
                "description": "用户标识",
            },
            {
                "name": "image_ref",
                "type": "string",
                "required": True,
                "description": "图片引用路径或URL",
            },
            {
                "name": "category",
                "type": "string",
                "required": True,
                "description": "类别：上衣/下装/外套/鞋类/包饰",
            },
            {
                "name": "primary_color",
                "type": "string",
                "required": True,
                "description": "主色",
            },
            {
                "name": "secondary_colors",
                "type": "array",
                "required": False,
                "description": "辅助色列表",
            },
            {
                "name": "pattern",
                "type": "string",
                "required": False,
                "description": "图案：纯色/条纹/格子/印花/无",
            },
            {
                "name": "silhouette",
                "type": "string",
                "required": False,
                "description": "版型：修身/宽松/直筒/A字/Oversize",
            },
            {
                "name": "material_guess",
                "type": "string",
                "required": False,
                "description": "材质推测，标记unknown或置信度",
            },
            {
                "name": "season_tags",
                "type": "array",
                "required": False,
                "description": "季节标签：春/夏/秋/冬",
            },
            {
                "name": "style_tags",
                "type": "array",
                "required": False,
                "description": "风格标签：休闲/正式/运动/复古等",
            },
            {
                "name": "user_confirmed",
                "type": "boolean",
                "required": True,
                "description": "用户是否已确认识别结果",
            },
            {
                "name": "available_status",
                "type": "string",
                "required": True,
                "description": "可用状态：available/unavailable/lost",
            },
            {
                "name": "created_at",
                "type": "string",
                "required": True,
                "description": "创建时间 ISO8601",
            },
            {
                "name": "updated_at",
                "type": "string",
                "required": True,
                "description": "更新时间 ISO8601",
            },
        ],
    },
    "products": {
        "description": "商家商品主表",
        "fields": [
            {
                "name": "product_id",
                "type": "string",
                "required": True,
                "description": "商品唯一标识",
            },
            {
                "name": "merchant_id",
                "type": "string",
                "required": True,
                "description": "商家标识",
            },
            {
                "name": "sku_id",
                "type": "string",
                "required": True,
                "description": "SKU编号",
            },
            {
                "name": "product_name",
                "type": "string",
                "required": True,
                "description": "商品名称",
            },
            {
                "name": "category",
                "type": "string",
                "required": True,
                "description": "类别：上衣/下装/外套/鞋类/包饰",
            },
            {
                "name": "color_tags",
                "type": "array",
                "required": True,
                "description": "颜色标签",
            },
            {
                "name": "material",
                "type": "string",
                "required": False,
                "description": "材质",
            },
            {
                "name": "pattern",
                "type": "string",
                "required": False,
                "description": "图案",
            },
            {
                "name": "silhouette",
                "type": "string",
                "required": False,
                "description": "版型",
            },
            {
                "name": "style_tags",
                "type": "array",
                "required": False,
                "description": "风格标签",
            },
            {
                "name": "season_tags",
                "type": "array",
                "required": False,
                "description": "季节标签",
            },
            {
                "name": "scene_tags",
                "type": "array",
                "required": False,
                "description": "场景标签：上课/面试/社团活动等",
            },
            {
                "name": "image_ref",
                "type": "string",
                "required": False,
                "description": "商品图片引用",
            },
            {
                "name": "product_url",
                "type": "string",
                "required": False,
                "description": "商品链接，无则空",
            },
            {
                "name": "sale_status",
                "type": "string",
                "required": True,
                "description": "销售状态：on_sale/off_shelf/discontinued",
            },
            {
                "name": "data_type",
                "type": "string",
                "required": True,
                "description": "数据类型：REAL/SYNTHETIC_DEMO",
            },
            {
                "name": "rights_status",
                "type": "string",
                "required": True,
                "description": "图片权利状态：owned/demo_placeholder/external_licensed",
            },
            {
                "name": "updated_at",
                "type": "string",
                "required": True,
                "description": "更新时间 ISO8601",
            },
        ],
    },
    "product_variants": {
        "description": "商品变体表（尺码/颜色/价格/库存）",
        "fields": [
            {
                "name": "variant_id",
                "type": "string",
                "required": True,
                "description": "变体唯一标识",
            },
            {
                "name": "product_id",
                "type": "string",
                "required": True,
                "description": "关联商品ID",
            },
            {
                "name": "size_label",
                "type": "string",
                "required": True,
                "description": "尺码标签：S/M/L/XL/均码/38/39等",
            },
            {
                "name": "color_label",
                "type": "string",
                "required": False,
                "description": "颜色标签",
            },
            {
                "name": "price_fen",
                "type": "integer",
                "required": True,
                "description": "价格（分），缺失时标记为-1",
            },
            {
                "name": "stock_qty",
                "type": "integer",
                "required": True,
                "description": "库存数量，0表示无货",
            },
            {
                "name": "shipping_fee_fen",
                "type": "integer",
                "required": False,
                "description": "运费（分），unknown时标记为-1",
            },
            {
                "name": "inventory_status",
                "type": "string",
                "required": True,
                "description": "库存状态：in_stock/low_stock/out_of_stock/unknown",
            },
            {
                "name": "inventory_updated_at",
                "type": "string",
                "required": True,
                "description": "库存更新时间 ISO8601",
            },
        ],
    },
    "styling_sessions": {
        "description": "穿搭会话表",
        "fields": [
            {
                "name": "session_id",
                "type": "string",
                "required": True,
                "description": "会话唯一标识",
            },
            {
                "name": "user_id",
                "type": "string",
                "required": True,
                "description": "用户标识",
            },
            {
                "name": "anchor_item_id",
                "type": "string",
                "required": True,
                "description": "锚点衣物ID（用户上传的那件）",
            },
            {
                "name": "occasion",
                "type": "string",
                "required": True,
                "description": "场合：上课/面试/社团活动等",
            },
            {
                "name": "temperature_text",
                "type": "string",
                "required": False,
                "description": "温度或天气描述",
            },
            {
                "name": "budget_fen",
                "type": "integer",
                "required": True,
                "description": "最高预算（分）",
            },
            {
                "name": "size_requirements_json",
                "type": "object",
                "required": True,
                "description": "尺码需求：{上装:M, 下装:L, 鞋类:39}",
            },
            {
                "name": "hard_constraints_json",
                "type": "object",
                "required": True,
                "description": "硬约束：{排除颜色:[], 排除版型:[], 排除类别:[]}",
            },
            {
                "name": "soft_preferences_json",
                "type": "object",
                "required": False,
                "description": "软偏好：{风格:[], 优先使用已有:true}",
            },
            {
                "name": "excluded_attributes_json",
                "type": "object",
                "required": False,
                "description": "排除属性",
            },
            {
                "name": "locked_items_json",
                "type": "object",
                "required": False,
                "description": "锁定项：{sku_id: reason}",
            },
            {
                "name": "current_state",
                "type": "string",
                "required": True,
                "description": "当前状态：input→parsed→planned→validated→confirmed",
            },
            {
                "name": "created_at",
                "type": "string",
                "required": True,
                "description": "创建时间",
            },
            {
                "name": "updated_at",
                "type": "string",
                "required": True,
                "description": "更新时间",
            },
        ],
    },
    "outfit_plans": {
        "description": "穿搭方案表",
        "fields": [
            {
                "name": "plan_id",
                "type": "string",
                "required": True,
                "description": "方案唯一标识",
            },
            {
                "name": "session_id",
                "type": "string",
                "required": True,
                "description": "关联会话ID",
            },
            {
                "name": "plan_version",
                "type": "integer",
                "required": True,
                "description": "方案版本号",
            },
            {
                "name": "plan_label",
                "type": "string",
                "required": True,
                "description": "方案标签：已有优先/预算优先/风格优先",
            },
            {
                "name": "purchase_subtotal_fen",
                "type": "integer",
                "required": True,
                "description": "商品小计（分）",
            },
            {
                "name": "known_fee_fen",
                "type": "integer",
                "required": True,
                "description": "已知费用（分）",
            },
            {
                "name": "unknown_fee_note",
                "type": "string",
                "required": False,
                "description": "未知费用说明",
            },
            {
                "name": "validation_status",
                "type": "string",
                "required": True,
                "description": "校验状态：passed/failed/partial",
            },
            {
                "name": "validation_result_json",
                "type": "object",
                "required": True,
                "description": "校验结果明细",
            },
            {
                "name": "inventory_snapshot_at",
                "type": "string",
                "required": True,
                "description": "库存快照时间",
            },
            {
                "name": "created_at",
                "type": "string",
                "required": True,
                "description": "创建时间",
            },
        ],
    },
    "outfit_plan_items": {
        "description": "方案单品明细表",
        "fields": [
            {
                "name": "record_id",
                "type": "string",
                "required": True,
                "description": "记录唯一标识",
            },
            {
                "name": "plan_id",
                "type": "string",
                "required": True,
                "description": "关联方案ID",
            },
            {
                "name": "source_type",
                "type": "string",
                "required": True,
                "description": "来源：closet(已有)/merchant(商家)",
            },
            {
                "name": "source_item_id",
                "type": "string",
                "required": True,
                "description": "来源衣物ID或SKU",
            },
            {
                "name": "variant_id",
                "type": "string",
                "required": False,
                "description": "变体ID（商家商品）",
            },
            {
                "name": "outfit_role",
                "type": "string",
                "required": True,
                "description": "搭配角色：上衣/下装/外套/鞋类/包饰",
            },
            {
                "name": "quantity",
                "type": "integer",
                "required": True,
                "description": "数量",
            },
            {
                "name": "locked",
                "type": "boolean",
                "required": True,
                "description": "是否锁定",
            },
            {
                "name": "replacement_reason",
                "type": "string",
                "required": False,
                "description": "替换原因",
            },
        ],
    },
    "interaction_logs": {
        "description": "交互日志表",
        "fields": [
            {
                "name": "event_id",
                "type": "string",
                "required": True,
                "description": "事件唯一标识",
            },
            {
                "name": "session_id",
                "type": "string",
                "required": True,
                "description": "关联会话ID",
            },
            {
                "name": "action_type",
                "type": "string",
                "required": True,
                "description": "操作类型",
            },
            {
                "name": "parsed_operation_json",
                "type": "object",
                "required": True,
                "description": "解析后的结构化操作",
            },
            {
                "name": "state_before",
                "type": "object",
                "required": False,
                "description": "操作前状态",
            },
            {
                "name": "state_after",
                "type": "object",
                "required": False,
                "description": "操作后状态",
            },
            {
                "name": "result_status",
                "type": "string",
                "required": True,
                "description": "结果：success/failed/partial",
            },
            {
                "name": "error_code",
                "type": "string",
                "required": False,
                "description": "错误码",
            },
            {
                "name": "plan_version",
                "type": "integer",
                "required": False,
                "description": "关联方案版本",
            },
            {
                "name": "created_at",
                "type": "string",
                "required": True,
                "description": "创建时间",
            },
        ],
    },
}

for name, schema in schemas.items():
    path = os.path.join(SCHEMA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"saved: {path} ({len(schema['fields'])} fields)")

print("\nAll 7 schemas created.")
