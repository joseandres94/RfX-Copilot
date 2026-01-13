from abc import ABC, abstractmethod
from ...shared.entities.document import Document

class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> None:
        """Save document to repository"""
        pass

    @abstractmethod
    def read(self, document_id: str) -> Document:
        """Read document from repository"""
        pass
