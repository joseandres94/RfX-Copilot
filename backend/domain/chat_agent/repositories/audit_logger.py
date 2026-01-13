from abc import ABC, abstractmethod
from ....domain.shared.value_objects.session_id import SessionId

class AuditLogger(ABC):
    @abstractmethod
    def log(self, session_id: SessionId, event: str, payload: dict) -> None:
        """Log event"""
        pass
