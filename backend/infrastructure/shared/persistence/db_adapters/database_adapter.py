"""Abstract database adapter interface."""

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseAdapter(ABC):
    """Abstract interface for fdatabase adapters."""

    @abstractmethod
    async def get_session(self) -> AsyncSession:
        """Get an async database session."""

    @abstractmethod
    async def connect(self) -> AsyncSession:
        """Initialize database connection."""

    @abstractmethod
    async def disconnect(self) -> AsyncSession:
        """Close database connection."""

    @abstractmethod
    async def health_check(self) -> AsyncSession:
        """Check if database connection is healthy."""
