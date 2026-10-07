# garment_card_builder

## 能力
从单品图片中提取衣物特征，生成结构化衣物识别卡。

## 触发条件
隐私检查通过后，对衣物图片进行识别。

## 输入
- image_path: 图片文件路径
- user_id: 用户标识（可选）

## 输出
```json
{
  "item_id": "uuid",
  "category": "上衣",
  "primary_color": "白色",
  "secondary_colors": ["浅灰"],
  "pattern": "纯色",
  "silhouette": "宽松",
  "material_guess": {"value": "棉", "confidence": 0.7, "status": "model_guess"},
  "season_tags": ["春", "夏"],
  "style_tags": ["休闲", "基础款"],
  "brand_guess": {"value": "unknown", "confidence": 0, "status": "unknown"},
  "confidence_summary": {
    "category": 0.92,
    "color": 0.88,
    "pattern": 0.75,
    "silhouette": 0.65,
    "material": 0.45
  },
  "needs_user_confirmation": true,
  "suggested_edits": ["材质可能为棉混纺，请确认"]
}
```

## 规则
- 类别必须从[上衣, 下装, 外套, 鞋类, 包饰]中选择
- 主色使用标准颜色名称
- 材质、品牌等无法可靠确定时标记为unknown或model_guess
- 每个字段附带置信度评分
- 置信度低于0.6的字段必须提示用户确认
- 不得推测尺码、身高、体重或消费能力
- 不得使用身体羞辱语言

## 边界
- 无法识别被遮挡超过50%的衣物
- 对特殊材质（如高科技面料）识别准确率较低
- 无法区分相似颜色（如米色vs浅卡其色）时提供选项让用户选择
