from abc import ABC, abstractmethod
from typing import List
from ....domain.ingestion.entities.chunk import Chunk

class EmbeddingService(ABC):
    """Interface for embedding services"""
    @abstractmethod
    def create_embeddings(self, chunks: List[Chunk]) -> List[Chunk]:
        """Create embeddings for a list of chunks and return a list of chunks with the embeddings"""
        pass
