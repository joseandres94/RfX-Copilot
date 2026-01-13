import logging
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from enum import Enum
from dataclasses import is_dataclass, asdict

from ....domain.shared.repositories.deal_repository import DealRepository
from ....domain.shared.entities.deal import Deal, DealStatus, PipelineStep

logger = logging.getLogger(__name__)


def _make_json_serializable(obj):
    """Convert Enums and dataclasses to JSON-serializable types"""
    if isinstance(obj, Enum):
        return obj.value
    elif is_dataclass(obj):
        return {k: _make_json_serializable(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_json_serializable(item) for item in obj]
    else:
        return obj


class FileDealRepository(DealRepository):
    """
    File-based implementation of DealRepository.
    
    Stores deals as JSON files for simple persistence.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "data/deals")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, deal: Deal) -> None:
        """Saves a deal to the file system"""
        try:
            file_path = self.storage_path / f"{deal.id}.json"
            
            # Update timestamp
            deal.updated_at = datetime.now()
            
            # Prepare data for JSON (ensure all Enums and complex types are serializable)
            deal_data = {
                "id": deal.id,
                "filename": deal.filename,
                "file_path": deal.file_path,
                "status": deal.status.value,
                "current_step": deal.current_step.value,
                "created_at": deal.created_at.isoformat(),
                "updated_at": deal.updated_at.isoformat(),
                "document_id": deal.document_id,
                # Ensure deal_context_model_json is fully serializable (handles Enums in nested structures)
                "deal_context_model_json": _make_json_serializable(deal.deal_context_model_json) if deal.deal_context_model_json else None,
                "dic_markdown": deal.dic_markdown,
                "demo_brief_markdown": deal.demo_brief_markdown,
                "demo_brief_json": _make_json_serializable(deal.demo_brief_json) if deal.demo_brief_json else None,
                "gaps_markdown": deal.gaps_markdown,
                "gaps_json": _make_json_serializable(deal.gaps_json) if deal.gaps_json else None,
                "error_message": deal.error_message,
                "error_step": deal.error_step.value if deal.error_step else None,
            }
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(deal_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Deal saved: {deal.id}")
            
        except Exception as e:
            logger.error(f"Error saving deal {deal.id}: {e}", exc_info=True)
            raise
    
    def get(self, deal_id: str) -> Optional[Deal]:
        """Retrieves a deal from the file system"""
        try:
            file_path = self.storage_path / f"{deal_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                deal_data = json.load(f)
            
            # Reconstruct Deal
            deal = Deal(
                id=deal_data["id"],
                filename=deal_data["filename"],
                file_path=deal_data["file_path"],
                status=DealStatus(deal_data["status"]),
                current_step=PipelineStep(deal_data["current_step"]),
                created_at=datetime.fromisoformat(deal_data["created_at"]),
                updated_at=datetime.fromisoformat(deal_data["updated_at"]),
                document_id=deal_data.get("document_id"),
                deal_context_model_json=deal_data.get("deal_context_model_json"),
                dic_markdown=deal_data.get("dic_markdown"),
                demo_brief_markdown=deal_data.get("demo_brief_markdown"),
                demo_brief_json=deal_data.get("demo_brief_json"),
                gaps_markdown=deal_data.get("gaps_markdown"),
                gaps_json=deal_data.get("gaps_json"),
                error_message=deal_data.get("error_message"),
                error_step=PipelineStep(deal_data["error_step"]) if deal_data.get("error_step") else None,
            )
            
            return deal
            
        except Exception as e:
            logger.error(f"Error loading deal {deal_id}: {e}", exc_info=True)
            raise

