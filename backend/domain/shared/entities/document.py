from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Document:
    id: str
    filename: str
    content: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
