"""Audit logger for security and model decisions."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class AuditLogger:
    def __init__(self, log_path: str = "logs/audit.log") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, payload: dict, severity: str = "info") -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "event_type": event_type,
            "severity": severity,
            "payload": payload,
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
