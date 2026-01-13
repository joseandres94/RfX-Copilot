import logging
import pdfplumber
from io import BytesIO
import uuid
from typing import List

from ....domain.ingestion.services.document_parser import DocumentParser
from ....domain.shared.entities.document import Document as DocumentEntity
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFParser(DocumentParser):
    """Parser for PDF files using pdfplumber (preferred) or PyPDF2 (fallback)"""
    
    # Maximum file size: 50 MB
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def can_parse(self, filename: str) -> bool:
        """Check if file is a PDF"""
        return filename.lower().endswith('.pdf')
    
    def parse(self, file_content: bytes, filename: str) -> DocumentEntity:
        """
        Parse PDF file and extract text content.
        
        Uses pdfplumber if available (better text extraction), 
        falls back to PyPDF2 if pdfplumber is not available.
        """
        if not file_content:
            raise ValueError("File content is empty")
        
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.1f} MB")
        
        try:
            text_parts = []
        
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num} of {filename}: {e}")
                        continue
            
            if not text_parts:
                raise ValueError("No text content could be extracted from PDF")
            
            content = "\n\n".join(text_parts)
            
            return DocumentEntity(
                id=str(uuid.uuid4()),
                filename=filename,
                content=content.strip(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error parsing PDF {filename}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse PDF file: {str(e)}")
