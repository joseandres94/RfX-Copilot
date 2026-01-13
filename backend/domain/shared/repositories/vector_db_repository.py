from abc import ABC, abstractmethod
from typing import List
from ....domain.ingestion.entities.chunk import Chunk

class VectorDBRepository(ABC):
    """Repository for vector database"""
    @abstractmethod
    def store_embedded_chunks(self, collection_name: str, embedded_chunks: List[Chunk]) -> None:
        """Store embedded chunks in vector database"""
        pass

    @abstractmethod
    def search_chunks(self, collection_name: str, query: List[float]) -> List[Chunk]:
        """Search for relevant chunks in vector database"""
        pass

    @abstractmethod
    def get_chunks(self, collection_name: str, chunk_ids: List[str]) -> List[Chunk]:
        """Get chunks from a collection by their ids"""
        pass