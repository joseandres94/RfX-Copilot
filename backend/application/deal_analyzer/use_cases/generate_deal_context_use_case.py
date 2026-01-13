from enum import Enum
from typing import List
from dataclasses import asdict, is_dataclass
from ....domain.ingestion.entities.chunk import Chunk
from ....application.deal_analyzer.interfaces.deal_context_llm_provider import DealContextLLMProvider
from ....domain.deal_analyzer.entities.deal_context import DealContext

import logging
logger = logging.getLogger(__name__)

class GenerateDealContextUseCase:
    """Use case for generating a deal context"""
    def __init__(
        self,
        deal_context_llm_provider: DealContextLLMProvider,
    ):
        self.deal_context_llm_provider = deal_context_llm_provider

    def execute(
        self,
        list_chunks: List[Chunk]
    ) -> tuple[dict, List[str]]:
        try:
            # Generate deal context
            deal_context, relevant_rfx_chunks_ids = self.deal_context_llm_provider.generate_deal_context(list_chunks)

            # Check if deal context was generated
            if not deal_context:
                raise ValueError("Deal context not found in document")
            
            # Convert to JSON-serializable dict and then to JSON string
            serializable_dict = self._serialize_to_json_serializable(deal_context)

            return serializable_dict, relevant_rfx_chunks_ids
            
        except Exception as e:
            logger.error(f"Error generating deal context: {e}")
            raise e
    
    def _serialize_to_json_serializable(self, obj) -> dict:
        """Recursively convert dataclass and Enum objects to JSON-serializable dicts"""
        if isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return {k: self._serialize_to_json_serializable(v) for k, v in asdict(obj).items()}
        elif isinstance(obj, dict):
            return {k: self._serialize_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_to_json_serializable(item) for item in obj]
        else:
            return obj