# constraint_validator

## 能力
使用确定性逻辑逐套检查方案的预算、价格、尺码、库存等约束。

## 触发条件
搭配方案生成后，对方案进行完整性校验。

## 输入
- plan: 单个搭配方案
- variants: 商品变体详情
- requirements: 需求解析结果

## 输出
```json
{
  "plan_id": "uuid",
  "validation_status": "passed",
  "checks": [
    {"check": "budget", "passed": true, "evidence": "purchase_subtotal=35800 <= budget=50000"},
    {"check": "price_exists", "passed": true, "evidence": "all items have price_fen > 0"},
    {"check": "size_match", "passed": true, "evidence": "上衣M, 下装L, 鞋类39 all matched"},
    {"check": "stock_positive", "passed": true, "evidence": "all variant stock_qty > 0"},
    {"check": "sale_status", "passed": true, "evidence": "all products on_sale"},
    {"check": "lock_honored", "passed": true, "evidence": "locked items preserved"},
    {"check": "exclude_respected", "passed": true, "evidence": "no excluded colors/silhouettes"},
    {"check": "source_verified", "passed": true, "evidence": "all from closet or catalog"}
  ],
  "failed_reasons": [],
  "warnings": [
    {"check": "shipping_fee", "level": "info", "message": "部分商品运费未知，最终金额待确认"}
  ]
}
```

## 校验项
- 预算：商品小计 <= 用户预算
- 价格存在：所有待购买商品价格 > 0
- 尺码匹配：每个品类有对应尺码且库存 > 0
- 库存为正：所有变体库存 > 0
- 销售状态：所有商品状态为 on_sale
- 锁定项：用户锁定的单品必须保留
- 排除项：不包含用户排除的颜色/版型/类别
- 商品来源：所有商品来自closet或已验证的catalog

## 规则
- 金额计算不得交给大模型心算，必须使用确定性代码
- 所有金额以分为整数保存和计算
- 校验失败时返回具体失败原因和证据字段
- 部分通过时标记为partial并列出未通过项

## 边界
- 不验证商品图片与实物一致性
- 不验证商品链接有效性
- 尺码合身度只检查库存存在性，不保证真实合身
