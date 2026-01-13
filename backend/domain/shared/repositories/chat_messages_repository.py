from abc import ABC, abstractmethod
from typing import List
from ..entities.chat_message import ChatMessage
from ..value_objects.session_id import SessionId
from ..value_objects.language import Language


class ChatMessagesRepository(ABC):
    """Interface for chat messages repository."""

    @abstractmethod
    async def create_session(self, session_id: SessionId, language: Language) -> None:
        """Create a new chat session."""
        pass

    @abstractmethod
    async def save_message(self, message: ChatMessage) -> None:
        """Save a chat message to the repository.
        
        Args:
            message: The chat message entity to save.
        """
        pass

    @abstractmethod
    async def get_history_messages(self, session_id: SessionId) -> List[ChatMessage]:
        """Get all messages for a session.
        
        Args:
            session_id: The session ID to retrieve messages for.
            
        Returns:
            List of chat messages for the session.
        """
        pass
    