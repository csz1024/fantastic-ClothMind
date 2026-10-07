# window_board_builder

## 能力
使用真实衣物图片和商品图片生成平铺搭配板或数字橱窗展示。

## 触发条件
方案通过校验后，生成可视化展示。

## 输入
- plan: 已通过校验的搭配方案
- item_images: 单品图片路径/URL映射
- display_mode: 展示模式（grid/collage/window）

## 输出
```json
{
  "board_type": "collage",
  "image_ref": "generated://outfit-board-uuid.png",
  "items": [
    {"role": "上衣", "source": "closet", "image": "user://item001.jpg", "position": [0, 0, 200, 200]},
    {"role": "下装", "source": "merchant", "image": "demo://OW-BTM-001.png", "position": [200, 0, 200, 200]}
  ],
  "disclaimer": "搭配示意图不代表真实上身效果",
  "status": "generated"
}
```

或降级输出：
```json
{
  "board_type": "card_grid",
  "image_ref": null,
  "items": [...],
  "disclaimer": "图片工具不可用，使用商品卡片展示",
  "status": "degraded"
}
```

## 规则
- 不得改变商品颜色、纹理、版型、配件数量和Logo
- 图片工具不可用时，使用商品卡片网格作为降级展示
- 不得声称已经生成效果图（当实际未生成时）
- AI生成氛围图只能作为辅助示意，不能代替真实商品图
- 赞助商品必须显著标识

## 边界
- 不保证拼贴图的美学质量
- 不生成真人上身效果图
- 不支持3D展示或虚拟试衣
