# interactive_replanner

## 能力
将用户自然语言操作转换为结构化指令，支持穿搭方案的交互式调整。

## 触发条件
用户在橱窗页进行锁定、替换、排除或预算调整时触发。

## 输入
- user_message: 用户自然语言输入
- current_plan: 当前方案状态
- available_inventory: 可用商品库存

## 输出
```json
{
  "parsed_operation": {
    "type": "REPLACE_ROLE",
    "target_role": "下装",
    "current_sku": "OW-BTM-001",
    "constraint": {"max_price_fen": 12000},
    "reason": "用户要求换成便宜一点的"
  },
  "system_understanding": "将当前方案中的下装（深蓝牛仔裤，159元）替换为价格不超过120元的下装",
  "ambiguous": false,
  "required_clarification": null
}
```

## 支持的操作类型
- LOCK_ITEM: 锁定某件商品（保留在当前方案中）
- UNLOCK_ITEM: 取消锁定
- REPLACE_ROLE: 替换某搭配角色的商品
- EXCLUDE_ATTRIBUTE: 排除某属性（如"不要黑色"）
- SET_MAX_BUDGET: 调整最高预算
- SET_SIZE: 修改某品类尺码
- UPDATE_STYLE: 更新风格偏好
- REFRESH_INVENTORY: 刷新库存状态
- REPLAN: 重新生成方案（保留锁定项）

## 规则
- 执行前显示系统理解的操作，等待用户确认
- 存在歧义时先询问，不猜测执行
- 每次修改后重新检索、计算和校验，不能只修改文案
- 替换商品时优先保留用户锁定项
- 库存变化时保留有效锁定项，只替换失效商品

## 边界
- 不支持模糊的颜色描述（如"深一点的蓝"）
- 不支持情感化描述（如"要有气质一点的"）
- 不记住跨会话的偏好
