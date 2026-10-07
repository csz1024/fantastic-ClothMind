# shopping_list_builder

## 能力
生成最终的购物意向清单，区分已有衣物和待购买商品。

## 触发条件
用户确认方案后，生成购物清单。

## 输入
- confirmed_plan: 用户确认的方案
- variants: 商品变体详情
- inventory_snapshot: 库存快照时间

## 输出
```json
{
  "list_id": "uuid",
  "status": "意向清单已生成",
  "closet_items": [
    {"item_id": "C001", "name": "白色T恤", "role": "上衣", "image": "user://item001.jpg"}
  ],
  "purchase_items": [
    {
      "sku_id": "OW-BTM-001",
      "variant_id": "V014",
      "name": "深蓝直筒牛仔裤",
      "role": "下装",
      "size": "L",
      "price_fen": 15900,
      "quantity": 1,
      "subtotal_fen": 15900,
      "image": "demo://OW-BTM-001.png",
      "product_url": "https://demo.example.com/OW-BTM-001",
      "stock_status": "in_stock"
    }
  ],
  "financial_summary": {
    "purchase_subtotal_fen": 35800,
    "known_fee_fen": 0,
    "unknown_fee_note": "部分商品运费待确认",
    "final_amount_determined": false,
    "message": "当前商品小计符合预算，最终支付金额仍需确认运费。"
  },
  "inventory_snapshot_at": "2026-10-07T19:00:00",
  "pending_confirmations": [
    "运费未知：OW-BTM-004等2件商品运费待确认",
    "尺码合身度仅供参考，建议对照尺码表"
  ],
  "disclaimer": "本清单为购物意向，不构成下单。价格、库存以购买前复核为准。"
}
```

## 规则
- 用户已有衣物不计入购买金额，但不能显示为商品免费
- 预算结果必须区分：商品小计、已知运费、其他已知费用、未知费用
- 运费未知时只能写"当前商品小计符合预算，最终支付金额仍需确认运费"
- 不能写"总价保证不超过预算"
- 没有支付接口时，最终状态只能是"购物意向清单已生成"
- 有真实链接时才显示前往商品页按钮

## 边界
- 不自动下单或支付
- 不自动联系商家
- 库存快照时间后发生的库存变化不自动更新
