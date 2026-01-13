import os
import json
from datetime import datetime, timezone
from pathlib import Path
from ....domain.chat_agent.repositories.audit_logger import AuditLogger
from ....domain.shared.value_objects.session_id import SessionId


class AuditLoggerRepository(AuditLogger):
    def __init__(self):
        self.base_dir = Path(os.getenv("DATA_DIR", "data/logs"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def log(self, session_id: SessionId, event: str, payload: dict) -> None:
        """Log event"""
        now = datetime.now(timezone.utc)
        record = {
            "session_id": session_id.value,
            "type": event,
            "ts": now.isoformat(),
            **payload
        }
        path = self.base_dir / f"{now.date()}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
