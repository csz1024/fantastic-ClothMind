"""input_privacy_audit：隐私检查。

本地 MVP 无云端视觉检测器。行为分三种模式（如实记录，不假装检测）：
- mode="manual"：返回 passed=False 且 requires_user_confirmation=True，
  由前端引导用户确认"照片仅含衣物、无他人人脸/证件/地址"，确认后才继续。
- mode="vision"：如果部署环境提供了 detector(image_path)->[risk]，则调用真实检测。
- mode="demo"：演示流水线使用，直接标记过审并记录"未执行真实视觉检测"。

注意：任何模式下都不得分析人脸身份或人体特征。
"""

from __future__ import annotations

import os
from typing import Callable, Optional

RiskDetector = Optional[Callable[[str], list]]


def audit_image(
    image_path: str,
    mode: str = "manual",
    detector: RiskDetector = None,
    user_confirmed: bool = False,
) -> dict:
    """检查图片隐私。返回结构化的 passed/risks/action/message。"""
    if mode == "demo":
        return {
            "passed": True,
            "risks": [],
            "action": "continue",
            "message": "[演示模式] 未执行真实视觉检测，仅按演示数据过审。",
            "mode": mode,
        }

    if not image_path:
        return {
            "passed": False,
            "risks": [{"type": "missing_image"}],
            "action": "pause",
            "message": "未收到图片文件，无法继续。",
            "mode": mode,
        }

    if mode == "vision" and detector is not None:
        try:
            risks = detector(image_path)
            passed = len(risks) == 0
            return {
                "passed": passed,
                "risks": risks,
                "action": "continue" if passed else "pause",
                "message": "视觉隐私检测通过。"
                if passed
                else "检测到隐私风险，请更换或裁剪图片。",
                "mode": mode,
            }
        except Exception as exc:
            return {
                "passed": False,
                "risks": [{"type": "detector_error", "detail": str(exc)}],
                "action": "pause",
                "message": "隐私检测器执行失败，请人工确认图片无隐私信息后继续。",
                "mode": mode,
            }

    if mode == "demo":
        return {
            "passed": True,
            "risks": [],
            "action": "continue",
            "message": "[演示模式] 未执行真实视觉检测，仅按演示数据过审。",
            "mode": mode,
        }

    # 默认 manual：由用户确认
    return {
        "passed": bool(user_confirmed),
        "risks": [] if user_confirmed else [{"type": "pending_user_confirmation"}],
        "action": "continue" if user_confirmed else "pause",
        "message": "请确认照片仅包含衣物单品，不含他人人脸、证件、快递单、门牌等隐私信息。"
        if not user_confirmed
        else "用户已确认图片无隐私信息。",
        "mode": mode,
    }
