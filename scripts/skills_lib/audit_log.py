"""audit_logger：结构化执行日志。

所有分析流水线事件都会写入 logs/ 下的 JSONL 文件。
隐私约束：不写入原始图片二进制或人脸等隐私数据。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


class AuditLogger:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.path = os.path.join(log_dir, "execution_audit.jsonl")

    def log(
        self,
        event_type: str,
        session_id: str,
        operation: dict,
        state_before: dict | None = None,
        state_after: dict | None = None,
    ) -> dict:
        record = {
            "event_id": _gen_id("evt"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "operation": operation,
            "state_before": _sanitize(state_before),
            "state_after": _sanitize(state_after),
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {
            "event_id": record["event_id"],
            "logged": True,
            "timestamp": record["timestamp"],
        }


def _gen_id(prefix: str) -> str:
    import random
    import string

    return (
        prefix
        + "-"
        + "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(12)
        )
    )


def _sanitize(obj):
    """递归去除日志中的敏感内容占位（演示实现）。"""
    return obj
