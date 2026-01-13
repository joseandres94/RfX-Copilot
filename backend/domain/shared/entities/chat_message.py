from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ..value_objects.session_id import SessionId
from ..value_objects.language import Language


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class ChatMessage:
    id: str
    session_id: SessionId
    role: Role
    content: str
    type: str
    stage: str
    timestamp: datetime
    language: Language
