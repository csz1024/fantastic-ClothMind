# hard_constraint_filter

## 能力
按硬约束逐条过滤商品，排除不符合条件的商品。

## 触发条件
需求解析完成后，对商品库进行硬约束过滤。

## 输入
- products: 商品列表
- variants: 变体列表
- constraints: 硬约束条件
  - exclude_colors: 排除颜色列表
  - exclude_silhouettes: 排除版型列表
  - exclude_categories: 排除类别列表
  - max_budget_fen: 最大预算（分）
  - required_sizes: 必需尺码映射 {category: size}
  - locked_items: 锁定项列表

## 输出
```json
{
  "total": 57,
  "passed": 32,
  "failed": 25,
  "details": [
    {
      "variant_id": "V006",
      "sku_id": "OW-TOP-003",
      "checks": {
        "sale_status": {"passed": true},
        "size_available": {"passed": false, "reason": "M码库存为0"},
        "price_exists": {"passed": true},
        "exclude_color": {"passed": true},
        "budget": {"passed": true},
        "lock_honored": {"passed": true}
      },
      "overall": false
    }
  ]
}
```

## 过滤顺序（严格）
1. 是否下架/停产（sale_status != on_sale）
2. 对应尺码是否存在
3. 对应尺码库存是否大于零
4. 是否缺少价格（price_fen < 0）
5. 是否违反用户排除项（颜色/版型/类别）
6. 是否超过预算（price_fen > max_budget_fen）
7. 是否破坏用户锁定项（锁定项SKU必须保留）

## 规则
- 硬约束未通过的商品不能靠风格评分重新进入结果
- 金额计算使用整数分，不得交给大模型心算
- 锁定项即使违反其他约束也必须保留（标记为冲突）
- 赞助商品不获得特殊过滤豁免

## 边界
- 不检查商品图片真实性
- 不验证商品链接可访问性
- 尺码匹配为精确匹配，不支持模糊匹配（如M≈均码）
