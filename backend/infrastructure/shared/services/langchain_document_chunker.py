from typing import List
from uuid import uuid4
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ....domain.ingestion.services.document_chunker import DocumentChunker
from ....domain.shared.entities.document import Document
from ....infrastructure.shared.types.chunk import Chunk


class LangchainDocumentChunker(DocumentChunker):
    """Langchain document chunker"""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""], # Default separators for paragraph priority
            add_start_index=True # Optional: adds character start index
        )

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk a document into smaller parts.
        
        Args:
            document: Document entity
            
        Returns:
            List of chunks
        """
        chunks_doc = self.text_splitter.split_text(document.content)
        list_chunks = []
        for i, chunk in enumerate(chunks_doc):
            new_chunk = Chunk(
                id=str(uuid4()),
                document_id=document.id,
                filename=document.filename + "_" + str(i),
                content=chunk,
                embedding=None
            )
            list_chunks.append(new_chunk)
        return list_chunks
