from datetime import datetime
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ....domain.shared.entities.chat_message import ChatMessage, Role
from ....domain.shared.value_objects.session_id import SessionId
from ....domain.shared.value_objects.language import Language
from ....infrastructure.chat_agent.models.chat_models import ChatMessageModel, ChatSessionModel, RoleModel
from ....domain.shared.repositories.chat_messages_repository import ChatMessagesRepository

import logging
logger = logging.getLogger(__name__)

class SQLChatRepository(ChatMessagesRepository):
    """Repository for chat messages"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, session_id: SessionId, language: Language) -> None:
        """Create a new chat session."""
        self.db_session.add(ChatSessionModel(id=session_id.value, created_at=datetime.now(), language=language.value))
        try:
            await self.db_session.commit()
        except Exception as e:
            error_message = f"Error creating session: {e}"  
            logger.error(error_message)
            await self.db_session.rollback()
            raise Exception(error_message)

    async def save_message(self, message: ChatMessage) -> None:
        """Save a chat message to the repository."""
        # Convert domain Role to model RoleModel
        role_model = RoleModel[message.role.name]
        message_model = ChatMessageModel(
            id=message.id,
            session_id=message.session_id.value,
            role=role_model,
            content=message.content,
            type=message.type,
            stage=message.stage,
            language=message.language,
            timestamp=message.timestamp
        )

        self.db_session.add(message_model)
        try:
            await self.db_session.commit()
        except Exception as e:
            logger.error(f"Error committing message: {e}")
            await self.db_session.rollback()
            raise e

    async def get_history_messages(self, session_id: SessionId) -> List[ChatMessage]:
        """Get all messages for a session."""
        stmt = select(ChatMessageModel).where(ChatMessageModel.session_id == session_id.value).order_by(ChatMessageModel.timestamp.asc())
        result = await self.db_session.execute(stmt)
        sql_messages = result.scalars().all()

        # Return list of ChatMessage entities
        return [ChatMessage(
            id=msg.id,
            session_id=SessionId(msg.session_id),
            role=Role[msg.role.name],  # Convert model RoleModel to domain Role
            content=msg.content,
            type=msg.type,
            stage=msg.stage,
            language=msg.language,
            timestamp=msg.timestamp
        ) for msg in sql_messages]
