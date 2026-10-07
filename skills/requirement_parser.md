# requirement_parser

## 能力
解析用户填写的表单和自然语言输入，输出结构化的穿搭需求。

## 触发条件
用户确认衣物卡后，收集穿搭场景需求。

## 输入
- 表单数据或自然语言文本
- 当前已确认的衣物卡（可选）

## 输出
```json
{
  "occasion": "面试",
  "temperature_text": "15-20度，秋季",
  "budget_fen": 30000,
  "size_requirements": {
    "上衣": "M",
    "下装": "L",
    "鞋类": "40"
  },
  "hard_constraints": {
    "exclude_colors": ["红色", "荧光色"],
    "exclude_silhouettes": ["Oversize"],
    "exclude_categories": [],
    "max_budget_fen": 30000
  },
  "soft_preferences": {
    "styles": ["正式", "简约"],
    "prioritize_closet": true,
    "color_preference": ["黑白灰", "藏蓝"]
  },
  "locked_items": {},
  "excluded_attributes": {},
  "missing_required": [],
  "conflicts": []
}
```

## 规则
- 场合必须从[上课与日常通勤, 面试与答辩, 社团活动与普通社交]中选择
- 不得根据照片推测尺码，必须向用户询问
- 缺少影响当前方案的必要信息时才进行追问
- 预算以分为单位存储，显示时转换为元
- 硬约束与软偏好必须明确分离
- 检测到冲突时列出并要求用户取舍

## 边界
- 不支持极端天气（如-30度或50度）的特殊穿搭
- 不支持需要特殊装备的场合（如登山、潜水）
- 不推断用户的性别、年龄或职业
