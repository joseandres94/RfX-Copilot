"""PostgreSQL database adapter implementation."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .base_sqlalchemy_adapter import BaseSQLAlchemyAdapter


class PostgreSQLAdapter(BaseSQLAlchemyAdapter):
    """PostgreSQL database adapter using SQLAlchemy async."""

    def __init__(
        self, database_url: str, pool_size: int = 10, max_overflow: int = 20
    ) -> None:
        super().__init__()
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    def _create_engine(self) -> AsyncEngine:
        """Create PostgreSQL engine with connection pooling."""
        return create_async_engine(
            self.database_url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            echo=False,  # Set to True for SQL query logging
        )
   
    async def connect(self) -> None:
        """Initialize database connection and create tables."""
        await super().connect()

        # Create tables if they don't exist
        # PostgreSLQ has foreign key constraints enabled by default
        if self._engine is not None:
            async with self._engine.begin() as conn:
                from ...database import Base

                await conn.run_sync(Base.metadata.create_all)
                