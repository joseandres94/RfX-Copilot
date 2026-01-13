from abc import ABC, abstractmethod

from ....domain.shared.entities.chat_message import ChatMessage
from ....domain.ingestion.entities.chunk import Chunk
from typing import List

class ChatLLMProvider(ABC):
    """Interface for Chat LLM providers"""
    @abstractmethod
    def generate_response(
        self, 
        chat_message: ChatMessage, 
        history_messages: List[ChatMessage], 
        relevant_chunks_query: List[Chunk],
        deal_context: dict,
        relevant_rfx_chunks: List[dict],
        demo_brief: dict,
        gaps: dict,
    ) -> str:
        """Generate a response to a user query"""
        pass
