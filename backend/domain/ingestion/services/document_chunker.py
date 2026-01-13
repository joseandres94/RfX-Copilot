from abc import ABC, abstractmethod
from typing import List
from ....domain.shared.entities.document import Document
from ....domain.ingestion.entities.chunk import Chunk


class DocumentChunker(ABC):
    """Interface for document chunkers"""
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """Chunk a document into smaller parts and return a list of chunks"""
        pass
    