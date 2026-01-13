import asyncio
import logging
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, UploadFile, Query, File, Form, BackgroundTasks

from ....domain.shared.entities.deal import Deal, DealStatus, PipelineStep
from ....domain.shared.repositories.deal_repository import DealRepository
from ....domain.shared.repositories.event_store import EventStore
from ....application.pipeline.pipeline_runner import PipelineRunner
from ....interface.dependencies import get_deal_repository, get_event_store, get_pipeline_runner
from ...schemas.deal_schemas import DealCreateResponse, DealStatusResponse, PipelineEventSchema

logger = logging.getLogger(__name__)

# Router initialization
router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=DealCreateResponse)
async def create_deal(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form(...),
    language: str = Form(...),
    deal_repository: DealRepository = Depends(get_deal_repository),
    pipeline_runner: PipelineRunner = Depends(get_pipeline_runner),
) -> DealCreateResponse:
    """
    Creates a new deal from an RfX file and starts the pipeline in the background.
    
    The file is saved temporarily and processed asynchronously.
    
    Args:
        file: RfX file (PDF, DOCX, TXT)
        
    Returns:
        DealCreateResponse with the generated deal_id
    """
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".txt"}
    file_extension = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Generate deal_id
        deal_id = session_id
        
        # Read file content
        file_content = await file.read()
        
        # Save file temporarily
        upload_path = Path("data/uploads")
        upload_path.mkdir(parents=True, exist_ok=True)
        file_path = upload_path / f"{deal_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create deal
        deal = Deal(
            id=deal_id,
            filename=file.filename,
            file_path=str(file_path),
            status=DealStatus.PROCESSING,
            current_step=PipelineStep.INGESTION,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # Save deal
        deal_repository.save(deal)
        
        logger.info(f"Deal created: {deal_id} for file {file.filename}")
        
        # Add pipeline to background tasks
        # Run in thread to avoid blocking
        background_tasks.add_task(
            _run_pipeline_sync,
            pipeline_runner,
            deal_id,
            file_content
        )
        
        logger.info(f"Pipeline added to background tasks for deal {deal_id}")
        
        return DealCreateResponse(deal_id=deal_id)
        
    except Exception as e:
        logger.error(f"Error creating deal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating deal: {str(e)}")


@router.get("/{deal_id}", response_model=DealStatusResponse)
async def get_deal_status(
    deal_id: str,
    since_event_id: Optional[int] = Query(default=0, description="Return only events with ID greater than this value"),
    deal_repository: DealRepository = Depends(get_deal_repository),
    event_store: EventStore = Depends(get_event_store),
) -> DealStatusResponse:
    """
    Gets the current status of a deal and its events.
    
    Allows polling from the frontend to show real-time progress.
    Use the since_event_id parameter to get only new events.
    
    Args:
        deal_id: Deal ID
        since_event_id: Optional, return only events with ID > this value
        
    Returns:
        DealStatusResponse with current status and events
    """
    try:
        # Retrieve deal
        deal = deal_repository.get(deal_id)
        
        if not deal:
            raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
        
        # Retrieve events
        events = event_store.get_events(deal_id, since_event_id=since_event_id)
        
        # Convert events to schema
        event_schemas = [
            PipelineEventSchema(
                id=event.id,
                timestamp=event.timestamp,
                type=event.type.value,
                step=event.step,
                message=event.message,
                payload=event.payload
            )
            for event in events
        ]
        
        # Build response
        response = DealStatusResponse(
            deal_id=deal.id,
            status=deal.status.value,
            current_step=deal.current_step.value,
            filename=deal.filename,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            events=event_schemas,
            error_message=deal.error_message,
            deal_context_available=deal.deal_context_model_json is not None,
            dic_available=deal.dic_markdown is not None,
            demo_brief_available=deal.demo_brief_markdown is not None,
            gaps_available=deal.gaps_markdown is not None,
            # Include markdown outputs if available
            dic_markdown=deal.dic_markdown,
            demo_brief_markdown=deal.demo_brief_markdown,
            gaps_markdown=deal.gaps_markdown,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deal status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting deal status: {str(e)}")


def _run_pipeline_sync(pipeline_runner: PipelineRunner, deal_id: str, file_content: bytes) -> None:
    """
    Synchronous wrapper to run the async pipeline.
    
    BackgroundTasks in FastAPI work better with sync functions.
    We create a new event loop here to run the async pipeline.
    """
    try:
        logger.info(f"Background task started for deal {deal_id}")
        
        # Create and run in new event loop
        asyncio.run(pipeline_runner.run_pipeline(deal_id, file_content))
        
        logger.info(f"Background task completed for deal {deal_id}")
        
    except Exception as e:
        logger.error(f"Error in background task for deal {deal_id}: {e}", exc_info=True)
