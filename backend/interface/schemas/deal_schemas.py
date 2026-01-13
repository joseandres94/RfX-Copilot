from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class DealCreateResponse(BaseModel):
    """Response when creating a deal"""
    deal_id: str


class PipelineEventSchema(BaseModel):
    """Schema for a pipeline event"""
    id: int
    timestamp: datetime
    type: str  # "info" | "result" | "error"
    step: str
    message: str
    payload: Optional[Dict[str, Any]] = None


class DealStatusResponse(BaseModel):
    """Response with the status of a deal and its events"""
    deal_id: str
    status: str  # "processing" | "ready" | "error"
    current_step: str
    filename: str
    created_at: datetime
    updated_at: datetime
    events: List[PipelineEventSchema]
    error_message: Optional[str] = None
    
    # Outputs availability flags
    deal_context_available: bool = False
    dic_available: bool = False
    demo_brief_available: bool = False
    gaps_available: bool = False
    
    # Markdown outputs (only included when available)
    dic_markdown: Optional[str] = None
    demo_brief_markdown: Optional[str] = None
    gaps_markdown: Optional[str] = None

