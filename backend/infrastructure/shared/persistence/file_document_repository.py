import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ....domain.ingestion.repositories.document_repository import DocumentRepository
from ....domain.shared.entities.document import Document

logger = logging.getLogger(__name__)


class FileDocumentRepository(DocumentRepository):
    """File-based implementation of DocumentRepository"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            storage_path: Path to store documents. Defaults to 'data/documents'
        """
        self.storage_path = Path(storage_path or "data/documents")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, document: Document) -> None:
        """
        Save document to file system.
        
        Documents are saved as JSON files with the following naming:
        {document.id}.json
        """
        try:
            # Create filename from document metadata
            file_path = self.storage_path / f"{document.id}.json"
            
            # Prepare document data
            document_data = {
                "id": document.id,
                "filename": document.filename,
                "content": document.content,
                "created_at": document.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Document saved: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving document: {e}", exc_info=True)
            raise

    def read(self, document_id: str) -> Document:
        """
        Read document from file system.
        
        Documents are read from JSON files with the following naming:
        {document.id}.json
        """
        try:
            # Create filename from document metadata
            file_path = self.storage_path / f"{document_id}.json"
            
            # Read from file
            with open(file_path, 'r', encoding='utf-8') as f:
                document_data = json.load(f)
            
            # Create document
            document = Document(
                id=document_data['id'],
                filename=document_data['filename'],
                content=document_data['content'],
                created_at=datetime.fromisoformat(document_data['created_at']),
                updated_at=datetime.fromisoformat(document_data['updated_at']),
            )
            
            return document
        except Exception as e:
            logger.error(f"Error reading document: {e}", exc_info=True)
            raise