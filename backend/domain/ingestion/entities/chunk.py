from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chunk:
    id: str
    document_id: str
    filename: str
    content: str
    embedding: Optional[List[float]] = None