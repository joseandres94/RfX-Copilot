from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from sqlalchemy.types import Enum

from ...shared.base_model import BaseModel


class RoleModel(PyEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatSessionModel(BaseModel):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    language: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class ChatMessageModel(BaseModel):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String)
    role: Mapped[RoleModel] = mapped_column(Enum(RoleModel, native_enum=False))
    content: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    stage: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)