from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class DealStatus(Enum):
    """Possible statuses for a Deal"""
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class PipelineStep(Enum):
    """Pipeline steps"""
    INGESTION = "ingestion"
    DEAL_ANALYZER = "deal_analyzer"
    SUMMARIZER = "summarizer"
    SOLUTION_ARCHITECT = "solution_architect"
    ENGAGEMENT_MANAGER = "engagement_manager"
    COMPLETED = "completed"


@dataclass
class Deal:
    """
    Deal entity that represents an RfX in processing.

    This entity contains the pipeline state and the outputs generated
    by each agent in the flow.
    """
    id: str
    filename: str
    file_path: str
    status: DealStatus
    current_step: PipelineStep
    created_at: datetime
    updated_at: datetime
    
    # Outputs from each pipeline step
    document_id: Optional[str] = None
    deal_context_model_json: Optional[dict] = None
    relevant_rfx_chunks_ids: Optional[List[str]] = None
    dic_markdown: Optional[str] = None
    demo_brief_markdown: Optional[str] = None
    demo_brief_json: Optional[dict] = None
    gaps_markdown: Optional[str] = None
    gaps_json: Optional[dict] = None
    
    # Error tracking
    error_message: Optional[str] = None
    error_step: Optional[PipelineStep] = None

