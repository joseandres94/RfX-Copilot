from pydantic import BaseModel, Field
from typing import Literal, Optional


# Classes definition
class ChatRequest(BaseModel):
    """Request schema for the chat"""
    session_id: str = Field(..., description="The session ID")
    text_message: str = Field(..., description="The text message")
    language: Literal["English", "Svenska"] = Field("English", description="The language")
    deal_id: Optional[str] = Field(None, description="Optional: Deal ID for RAG context")


class ChatResponse(BaseModel):
    """Response schema for the chat"""
    answer: str = Field("", description="The answer to the user query")
    stage: Literal["welcome", "summary", "qa"] = Field("welcome", description="The stage of the chat")