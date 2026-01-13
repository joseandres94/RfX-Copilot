import os
from datetime import datetime, timezone
import json
from pathlib import Path
from ....domain.chat_agent.repositories.consent_repository import ConsentRepository
from ....domain.chat_agent.entities.consent import Consent
from ....domain.shared.value_objects.session_id import SessionId


class FileConsentRepository(ConsentRepository):
    def __init__(self):
        self.base_dir = Path(os.getenv("DATA_DIR", "data/consents"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, consent: Consent) -> bool:
        """Save consent to file"""
        now = datetime.now(timezone.utc)
        record = {
            "type": "consent_captured",
            "ts": now.isoformat(),
            "session_id": consent.session_id.value,
            "patient_name": consent.patient_name,
            "method": consent.method.value,
            "timestamp": consent.timestamp.isoformat()
        }
        path = self.base_dir / f"{consent.session_id.value}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True

    def get(self, session_id: SessionId) -> Consent:
        """Get consent from file"""
        path = self.base_dir / f"{session_id.value}.jsonl"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)
                return Consent.from_dict(record)
        raise ValueError(f"Consent not found for session_id: {session_id}")

    def delete(self, session_id: SessionId) -> None:
        """Delete consent from file"""
        path = self.base_dir / f"{session_id}.jsonl"
        if path.exists():
            path.unlink()