from dataclasses import dataclass
from datetime import datetime
from ....domain.shared.value_objects.session_id import SessionId
from ..value_objects.consent_method import ConsentMethod


@dataclass
class Consent:
    """Consent entity"""
    patient_name: str
    session_id: SessionId
    method: ConsentMethod
    timestamp: datetime

    def __post_init__(self):
        """Business rules validation"""
        if not self.patient_name.strip():
            raise ValueError("Patient name is required")

        if not self.session_id:
            raise ValueError("Session ID is required")
        
        if self.timestamp > datetime.now():
            raise ValueError("Timestamp cannot be in the future")
    
    def is_valid(self) -> bool:
        """Valid consent if has a patient name and method"""
        return bool(self.patient_name.strip() and self.method)