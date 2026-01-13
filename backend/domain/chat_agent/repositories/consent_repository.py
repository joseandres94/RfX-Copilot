from abc import ABC, abstractmethod
from ..entities.consent import Consent
from ....domain.shared.value_objects.session_id import SessionId

class ConsentRepository(ABC):
    @abstractmethod
    def save(self, consent: Consent) -> bool:
        """Save consent to repository"""
        pass

    @abstractmethod
    def get(self, session_id: SessionId) -> Consent:
        """Get consent from repository"""
        pass

    @abstractmethod
    def delete(self, session_id: SessionId) -> None:
        """Delete consent from repository"""
        pass