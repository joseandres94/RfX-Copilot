import logging
import chardet
import uuid
from typing import List

from ....domain.ingestion.services.document_parser import DocumentParser
from ....domain.shared.entities.document import Document as DocumentEntity
from datetime import datetime

logger = logging.getLogger(__name__)


class TXTParser(DocumentParser):
    """Parser for plain text files with automatic encoding detection"""
    
    # Maximum file size: 10 MB (text files are usually smaller)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Common encodings to try (in order of preference)
    COMMON_ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def can_parse(self, filename: str) -> bool:
        """Check if file is a TXT"""
        return filename.lower().endswith('.txt')
    
    def parse(self, file_content: bytes, filename: str) -> DocumentEntity:
        """
        Parse TXT file and extract text content.
        
        Automatically detects encoding using chardet, with fallback to common encodings.
        """
        if not file_content:
            raise ValueError("File content is empty")
        
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.1f} MB")
        
        try:
            # Try to detect encoding
            encoding = self._detect_encoding(file_content)
            
            # Decode content
            try:
                content = file_content.decode(encoding)
            except (UnicodeDecodeError, LookupError) as e:
                logger.warning(f"Failed to decode with detected encoding {encoding}, trying fallbacks: {e}")
                # Try fallback encodings
                content = self._decode_with_fallbacks(file_content)
            
            if not content.strip():
                raise ValueError("Text file appears to be empty")
            
            return DocumentEntity(
                id=str(uuid.uuid4()),
                filename=filename,
                content=content.strip(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Error parsing TXT {filename}: {e}", exc_info=True)
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to parse TXT file: {str(e)}")
    
    def _detect_encoding(self, file_content: bytes) -> str:
        """
        Detect file encoding using chardet.
        
        Falls back to utf-8 if detection fails or confidence is low.
        """
        try:
            result = chardet.detect(file_content)
            if result and result.get('encoding') and result.get('confidence', 0) > 0.7:
                detected_encoding = result['encoding']
                logger.debug(f"Detected encoding: {detected_encoding} (confidence: {result.get('confidence', 0):.2f})")
                return detected_encoding
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}")
        
        # Default to utf-8
        return 'utf-8'
    
    def _decode_with_fallbacks(self, file_content: bytes) -> str:
        """
        Try to decode content using common encodings as fallback.
        
        Raises ValueError if all encodings fail.
        """
        last_error = None
        
        for encoding in self.COMMON_ENCODINGS:
            try:
                return file_content.decode(encoding)
            except (UnicodeDecodeError, LookupError) as e:
                last_error = e
                continue
        
        raise ValueError(
            f"Failed to decode text file with any of the attempted encodings: {self.COMMON_ENCODINGS}. "
            f"Last error: {str(last_error)}"
        )
