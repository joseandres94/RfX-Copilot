"""Base SQLAlchemy adapter implementation."""

from abc import abstractmethod

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from .database_adapter import DatabaseAdapter


class BaseSQLAlchemyAdapter(DatabaseAdapter):
    """Base SQLAlchemy adapter with common session management."""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @abstractmethod
    def _create_engine(self) -> AsyncEngine:
        """Create database engine with database-specific configuration"""

    async def connect(self) -> None:
        """Initialize database connection."""
        if self._engine is None:
            self._engine = self._create_engine()

            self._session_factory = async_sessionmaker(
                bind=self._engine, class_=AsyncSession, expire_on_commit=False
            )

    async def disconnect(self) -> None:
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine=None
            self._session_factory=None

    async def get_session(self) -> AsyncSession:
        """Get a new async database session."""
        if self._session_factory is None:
            await self.connect()

        if self._session_factory is None:
            raise RuntimeError("Database connection not established")
        
        return self._session_factory()

    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            if self._engine is None:
                return False

            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False