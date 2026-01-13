from dataclasses import dataclass
from uuid import UUID


@dataclass
class SessionId:
    """Value object for session ID"""
    value: str

    def __post_init__(self):
        """Business rules validation"""
        if not self.value:
            raise ValueError("Session ID is required")
        try:
            # Validate UUID format
            UUID(self.value)
        except ValueError:
            raise ValueError("Session ID is not a valid UUID")