from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class EventType(Enum):
    """Types of pipeline events"""
    INFO = "info"
    RESULT = "result"
    ERROR = "error"


@dataclass
class PipelineEvent:
    """
    Pipeline event that represents an action or result during
    the execution of the Deal processing flow.
    
    These events allow the frontend to poll and show real-time progress.
    """
    id: int
    deal_id: str
    timestamp: datetime
    type: EventType
    step: str
    message: str
    payload: Optional[Dict[str, Any]] = None

