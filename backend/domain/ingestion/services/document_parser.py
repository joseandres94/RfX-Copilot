from abc import ABC, abstractmethod
from ...shared.entities.document import Document


class DocumentParser(ABC):
    """Interface for document parsers"""
    
    @abstractmethod
    def parse(self, file_content: bytes, filename: str) -> Document:
        """
        Parse a document and extract its content.
        
        Args:
            file_content: Raw bytes of the file
            filename: Name of the file (used to determine type)
            
        Returns:
            Document entity with extracted content
            
        Raises:
            ValueError: If file content is invalid or empty
            #NotImplementedError: If file type is not supported
            Exception: For parsing errors (corrupted files, etc.)
        """
        pass
    
    @abstractmethod
    def can_parse(self, filename: str) -> bool:
        """
        Check if this parser can handle the given file type.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if this parser can handle the file type
        """
        pass
