import os
from dotenv import load_dotenv
from typing import List, Protocol, cast
from ....domain.ingestion.entities.chunk import Chunk
from ....domain.shared.repositories.vector_db_repository import VectorDBRepository
import chromadb

# Get environment variables
load_dotenv()
CHROMA_HOST=os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT=os.getenv("CHROMA_PORT", "8000")


class ChromaDBClientProtocol(Protocol):
    """Protocol for ChromaDB client"""
    def get_or_create_collection(self, name: str) -> object:
        """Get or create a collection"""
        pass


class ChromaDBCollectionProtocol(Protocol):
    """Protocol for ChromaDB collection"""
    def upsert(self, ids: List[str], embeddings: List[List[float]]) -> None:
        """Upsert a chunk into a collection"""
        pass
    
    def query(self, query: List[float]) -> List[Chunk]:
        """Query a collection and return a list of chunks that match the query"""
        pass

    def get(self, chunk_ids: List[str]) -> List[Chunk]:
        """Get a chunk from a collection"""
        pass
    

class ChromaDBRepository(VectorDBRepository):
    """Repository for vector database"""
    def __init__(self):
        self._client: ChromaDBClientProtocol | None = None
        self._collection: ChromaDBCollectionProtocol | None = None

    def _get_client(self, collection_name: str) -> ChromaDBClientProtocol:
        if self._client is None:
            self._client = cast(ChromaDBClientProtocol, chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT))
            self._collection = self._client.get_or_create_collection(name=collection_name)
        return self._client

    def _get_collection(self, collection_name: str) -> ChromaDBCollectionProtocol:
        if self._collection is None:
            self._get_client(collection_name)
        if self._collection is None:
            raise ValueError(f"Failed to initialize ChromaDB collection: {collection_name}")
        return self._collection

    def store_embedded_chunks(self, collection_name: str, embedded_chunks: List[Chunk]) -> None:
        """Store embedded chunks in vector database"""
        collection = self._get_collection(collection_name)
        collection.upsert(
            ids=[chunk.id for chunk in embedded_chunks],
            embeddings=[chunk.embedding for chunk in embedded_chunks],
            documents=[chunk.content for chunk in embedded_chunks],
            metadatas=[{'document_id': chunk.document_id, 'filename': chunk.filename} for chunk in embedded_chunks]
        )

    def search_chunks(self, collection_name: str, query: List[float]) -> List[Chunk]:
        """Search for relevant chunks in vector database"""
        collection = self._get_collection(collection_name)
        results = collection.query(query, n_results=3)
        
        # ChromaDB returns nested lists: {'ids': [[...]], 'documents': [[...]], ...}
        # We need to access the first element of each list
        if not results['ids'] or not results['ids'][0]:
            return []
        
        return [
            Chunk(
                id=results['ids'][0][i],
                content=results['documents'][0][i],
                embedding=None,
                document_id=results['metadatas'][0][i]['document_id'],
                filename=results['metadatas'][0][i]['filename']
            ) for i in range(len(results['ids'][0]))
        ]

    def get_chunks(self, collection_name: str, chunk_ids: List[str]) -> List[Chunk]:
        """Get chunks from a collection by their ids"""
        collection = self._get_collection(collection_name)
        result = collection.get(ids=chunk_ids)
        
        # ChromaDB's get() returns flat lists: {'ids': [...], 'documents': [...], ...}
        if not result['ids']:
            return []
        
        return [
            Chunk(
                id=result['ids'][i],
                content=result['documents'][i],
                embedding=None,
                document_id=result['metadatas'][i]['document_id'],
                filename=result['metadatas'][i]['filename']
            ) for i in range(len(result['ids']))
        ]
