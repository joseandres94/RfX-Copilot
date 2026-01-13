"""SQLite database adapter implementation."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .base_sqlalchemy_adapter import BaseSQLAlchemyAdapter


class SQLiteAdapter(BaseSQLAlchemyAdapter):
    """SQLite database adapter using SQLAlchemy async."""

    def __init__(self, database_url: str = "sqlite+aiosqlite:///./chat_data.db") -> None:
        """Initialize SQLite adapter.

        Args:
            database_url: Database connection URL

        Raises:
            ValueError: If database_url is not a valid SQLite URL
        """
        if not database_url.startswith("sqlite+aiosqlite://"):
            raise ValueError("Invalid SQLite URL")
        self.database_url = database_url
    
    def _create_engine(self) -> AsyncEngine:
        """Create async SQLite engine."""
        return create_async_engine(
            self.database_url,
            echo=False,  # Set to True for SQL query logging
        )

    async def connect(self) -> None:
        """Initialize database connection and enable foreign key constraints."""
        await super().connect()

        # Enable foreign key constraints for SQLite
        if self._engine is not None:
            async with self._engine.begin() as conn:
                await conn.execute(text("PRAGMA foreign_keys=ON"))

                # Create tables if they don't exist
                from ...database import Base

                await conn.run_sync(Base.metadata.create_all)
