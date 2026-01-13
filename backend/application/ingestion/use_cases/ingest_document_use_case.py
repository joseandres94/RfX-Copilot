import logging
from typing import List
from backend.domain.shared.entities.document import Document
from backend.domain.ingestion.entities.chunk import Chunk
from backend.domain.ingestion.services.document_parser import DocumentParser
from backend.domain.ingestion.services.document_chunker import DocumentChunker
from backend.domain.shared.services.embedding_service import EmbeddingService
from backend.domain.ingestion.repositories.document_repository import DocumentRepository
from backend.domain.shared.repositories.vector_db_repository import VectorDBRepository

logger = logging.getLogger(__name__)

class IngestDocumentUseCase:
    """Use case for ingesting a document"""
    def __init__(
        self,
        document_parser: DocumentParser,
        document_chunker: DocumentChunker,
        embedding_service: EmbeddingService,
        vector_db_repository: VectorDBRepository,
        document_repository: DocumentRepository
    ):
        self.document_parser = document_parser
        self.document_chunker = document_chunker
        self.embedding_service = embedding_service
        self.vector_db_repository = vector_db_repository
        self.document_repository = document_repository

    def execute(self, deal_id: str, file_content: bytes, filename: str, collection_name: str) -> List[Chunk]:
        """Execute the use case"""

        try:
            # Parse document
            document = self.document_parser.parse(file_content, filename)
            document.id = deal_id

            # Chunk, embed and store chunks
            list_chunks = self._chunk_and_embed(document, collection_name)

            # Save document
            self.document_repository.save(document)

            # Return document
            return list_chunks

        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            raise e


    def _chunk_and_embed(self, document: Document, collection_name: str) -> List[Chunk]:
        """Chunk, embed and store chunks"""
        try:
            # Create chunks
            chunks = self.document_chunker.chunk(document)
            
            # Create embeddings for chunks
            embedded_chunks = self.embedding_service.create_embeddings(chunks)

            # Store embeddings
            self.vector_db_repository.store_embedded_chunks(collection_name=collection_name, embedded_chunks=embedded_chunks)

            return embedded_chunks

        except Exception as e:
            logger.error(f"Error chunking and embedding document: {e}")
            raise e
