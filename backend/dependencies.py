from functools import lru_cache
import logging
from typing import AsyncGenerator
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .infrastructure.shared.persistence.db_adapters.database_adapter import DatabaseAdapter
from .infrastructure.shared.persistence.db_adapters.sql_db_factory import create_database_adapter
from .infrastructure.shared.config.settings import LLMSettings, get_settings

logger = logging.getLogger(__name__)

@lru_cache
def get_database_adapter() -> DatabaseAdapter:
    """Get singleton database adapter instance."""
    settings = get_settings()

    return create_database_adapter(
        database_type=settings.database.database_type,
        database_url=settings.database.database_url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
    )

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session from the application state.

    This dependency provides a new database session for each request.
    The session is automatically closed when the request completes.

    Raises:
        HTTPException: If database connection is not available
    """
    from .infrastructure.shared.config.container import get_app_state

    app_state = get_app_state()

    if not app_state.is_initialized or app_state.database_adapter is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    # Create a new session for this request
    session = await app_state.database_adapter.get_session()

    try:
        yield session
    finally:
        await session.close()


@lru_cache
def get_llm_settings() -> LLMSettings:
    """Get LLM settings from shared configuration.

    Returns:
        LLM configuration settings
    """
    settings = get_settings()
    return settings.llm
