import logging
from typing import List, Optional
from pathlib import Path

from ....domain.ingestion.services.document_parser import DocumentParser
from ....domain.shared.entities.document import Document
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TXTParser

logger = logging.getLogger(__name__)


class DocumentParserService(DocumentParser):
    """
    Main document parser service that coordinates specific parsers.
    
    This service acts as a facade that routes files to the appropriate
    specialized parser based on file extension.
    """
    
    # Maximum file size: 50 MB (applied before parsing)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    
    def __init__(self, pdf_parser: PDFParser, docx_parser: DOCXParser, txt_parser: TXTParser):
        """Initialize the parser service with all available parsers"""
        self._parsers: List[DocumentParser] = [
            pdf_parser,
            docx_parser,
            txt_parser
        ]
    
    def can_parse(self, filename: str) -> bool:
        """
        Check if the file type is supported.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file type is supported
        """
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.ALLOWED_EXTENSIONS
    
    def parse(self, file_content: bytes, filename: str) -> Document:
        """
        Parse a document by routing it to the appropriate parser.
        
        Args:
            file_content: Raw bytes of the file
            filename: Name of the file (used to determine type)
            
        Returns:
            Document entity with extracted content
            
        Raises:
            ValueError: If file is invalid, unsupported, or parsing fails
        """
        # Validate inputs
        if not file_content:
            raise ValueError("File content cannot be empty")
        
        if not filename:
            raise ValueError("Filename is required")
        
        # Validate file size
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({len(file_content) / (1024*1024):.2f} MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / (1024*1024):.1f} MB)"
            )
        
        # Validate file extension
        if not self.can_parse(filename):
            file_ext = Path(filename).suffix.lower()
            raise ValueError(
                f"Unsupported file type: {file_ext}. "
                f"Supported types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Find appropriate parser
        parser = self._find_parser(filename)
        if not parser:
            raise ValueError(f"No parser available for file: {filename}")
        
        # Parse document
        try:
            logger.info(f"Parsing document: {filename} (size: {len(file_content)} bytes)")
            document = parser.parse(file_content, filename)
            logger.info(f"Successfully parsed document: {filename} (extracted {len(document.content)} characters)")
            return document
        except Exception as e:
            logger.error(f"Failed to parse document {filename}: {e}", exc_info=True)
            raise

    def _find_parser(self, filename: str) -> Optional[DocumentParser]:
        """
        Find the appropriate parser for the given filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            Parser instance if found, None otherwise
        """
        for parser in self._parsers:
            if parser.can_parse(filename):
                return parser
        
        return None
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported extensions (e.g., ['.pdf', '.docx', '.txt'])
        """
        return list(self.ALLOWED_EXTENSIONS)
