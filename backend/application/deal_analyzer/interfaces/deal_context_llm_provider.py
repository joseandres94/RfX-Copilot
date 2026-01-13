from abc import ABC, abstractmethod
from typing import List

from ....domain.ingestion.entities.chunk import Chunk
from ....domain.deal_analyzer.entities.deal_context import DealContext

class DealContextLLMProvider(ABC):
    """Interface for Deal Context LLM providers"""
    @abstractmethod
    def generate_deal_context(
        self, 
        list_chunks: List[Chunk],
    ) -> DealContext:
        """Generate a deal context"""
        pass
