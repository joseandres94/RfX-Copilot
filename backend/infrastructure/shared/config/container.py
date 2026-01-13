"""Application state and lifecycle management."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..persistence.db_adapters.database_adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


# Global application state
class ApplicationState:
    """Global application state container."""

    def __init__(self) -> None:
        self.database_adapter: DatabaseAdapter | None = None
        self.is_initialized = False


# Global state instance
app_state = ApplicationState()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager for startup and shutdown."""
    from ....dependencies import get_database_adapter

    # Startup
    try:
        # Initialize database adapter
        app_state.database_adapter = get_database_adapter()
        if app_state.database_adapter is not None:
            await app_state.database_adapter.connect()

        app_state.is_initialized = True
        print("✅ Database connection established")

        yield

    finally:
        # Shutdown
        if app_state.database_adapter:
            await app_state.database_adapter.disconnect()
            print("✅ Database connection closed")

        app_state.is_initialized = False

def get_app_state() -> ApplicationState:
    """Get the global application state."""
    return app_state
