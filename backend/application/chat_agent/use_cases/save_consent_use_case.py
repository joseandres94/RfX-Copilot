from datetime import datetime
from ....domain.shared.value_objects.session_id import SessionId
from ....domain.chat_agent.value_objects.consent_method import ConsentMethod
from ....domain.chat_agent.repositories.consent_repository import ConsentRepository
from ....domain.chat_agent.repositories.audit_logger import AuditLogger
from ....domain.chat_agent.entities.consent import Consent

import logging
logger = logging.getLogger(__name__)

class SaveConsentUseCase:
    """Use case for saving a consent"""
    def __init__(self, consent_repository: ConsentRepository, audit_logger: AuditLogger):
        self.consent_repository = consent_repository
        self.audit_logger = audit_logger

    def execute(
        self,
        patient_name: str,
        session_id: SessionId,
        method: ConsentMethod,
        timestamp: datetime
    ) -> bool:
        """Execute the use case"""
        consent = Consent(
            patient_name=patient_name,
            session_id=session_id,
            method=method,
            timestamp=timestamp
        )
        
        # Validate consent
        if not consent.is_valid():
            raise ValueError("Consent is not valid")

        # Save consent
        self.consent_repository.save(consent)
        
        # Save audit
        self.audit_logger.log(
            session_id=consent.session_id,
            event="consent_captured",
            payload={
                "patient_name": consent.patient_name,
                "session_id": consent.session_id.value,
                "method": consent.method.value,
                "timestamp": consent.timestamp.isoformat()
            }
        )
        return True
