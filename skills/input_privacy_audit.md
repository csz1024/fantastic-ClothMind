# input_privacy_audit

## 能力
检查用户上传的衣物单品照片是否包含明显人脸、证件、快递单、门牌或其他隐私信息。

## 触发条件
用户上传任何图片时自动触发。

## 输入
- image_path: 图片文件路径
- image_bytes: 图片二进制数据（可选）

## 输出
```json
{
  "passed": true,
  "risks": [],
  "action": "continue"
}
```

或

```json
{
  "passed": false,
  "risks": [
    {"type": "face", "confidence": 0.95, "region": "center"},
    {"type": "id_card", "confidence": 0.88, "region": "lower_right"}
  ],
  "action": "pause",
  "message": "检测到照片中包含人脸/证件信息。请裁剪为仅包含衣物的单品照片后重新上传。"
}
```

## 规则
- 不得分析人脸、身份或人体特征
- 不得识别照片中的人物身份
- 检测到风险时暂停视觉分析，提示用户裁剪或重新上传
- 只关注衣物本身，忽略背景中的非隐私信息
- 对模糊或不确定的隐私信息标记为"待确认"而非直接判定

## 边界
- 无法检测经过专业处理或极度模糊的隐私信息
- 不处理视频文件
- 不保存用户原始图片到日志（只保存分析结果）
