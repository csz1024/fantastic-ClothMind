# outfit_planner

## 能力
以用户确认的衣物为锚点，生成候选穿搭方案。

## 触发条件
硬约束过滤完成后，进行搭配组合规划。

## 输入
- anchor_item: 锚点衣物（用户上传的那件）
- closet_items: 用户已有衣物列表
- merchant_products: 通过硬约束的商家商品列表
- requirements: 需求解析结果
- locked_items: 锁定项

## 输出
```json
{
  "plans": [
    {
      "plan_id": "uuid",
      "plan_label": "已有优先",
      "items": [
        {"source": "closet", "item_id": "C001", "role": "上衣", "locked": false},
        {"source": "merchant", "sku_id": "OW-BTM-001", "variant_id": "V014", "role": "下装", "locked": false},
        {"source": "merchant", "sku_id": "OW-SHO-001", "variant_id": "V034", "role": "鞋类", "locked": false}
      ],
      "purchase_subtotal_fen": 35800,
      "reasoning": "使用用户已有的白色T恤，搭配深蓝牛仔裤和白色板鞋，符合上课通勤场景"
    }
  ],
  "coverage": {
    "roles_filled": ["上衣", "下装", "鞋类"],
    "roles_missing": ["外套"],
    "closet_usage": 1,
    "merchant_usage": 2
  }
}
```

## 规则
- 优先使用用户衣橱中的其他单品，再推荐商家商品
- 每套搭配最多包含5件单品
- 默认方案方向：已有衣物复用优先、预算节省优先、风格表达优先
- 只有存在真实差异且通过校验时才显示
- 不能自行宣布校验通过（需交给constraint_validator）
- 锚点衣物必须出现在每套方案中
- 赞助商品必须显著标识

## 边界
- 不生成虚构商品
- 不保证搭配的时尚性（只保证逻辑可穿性）
- 不支持跨季节混搭（如羽绒服+短裤）
