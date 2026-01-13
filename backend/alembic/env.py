"""Alembic environment configuration for database migrations.

This file configures Alembic to work with our async SQLAlchemy setup.
For SQLite, Alembic uses a synchronous engine for migrations.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from alembic import context

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import database configuration and models
from backend.dependencies import DATABASE_URL
from backend.infrastructure.chat_agent.models.chat_models import Base

# Import all models to ensure they're registered with Base.metadata
#from backend.infrastructure.chat_agent.models import chat_models  # noqa: F401

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Converts an asynchronous SQLite database URL to a synchronous version suitable for Alembic operations.
# Utilizes a synchronous engine for migrations as Alembic does not provide full compatibility with asynchronous SQLite drivers.
def get_sync_database_url() -> str:
    """Converts an async database URL to its synchronous form for Alembic.
    
    Additionally, ensures that SQLite file paths are absolute and standardized relative to the project root directory.
    This guarantees consistent operation of Alembic, regardless of the current working directory.
    """
    url = DATABASE_URL
    
    # Ensure SQLite file paths are absolute and normalized with respect to the project root directory.
    if "sqlite" in url.lower():
        # Parse the path segment from the URL.
        # Expected formats: sqlite:///path or sqlite+aiosqlite:///path
        if "///" in url:
            parts = url.split("///", 1)
            if len(parts) == 2:
                db_path = parts[1]
                
                # Remove redundant leading './', if present.
                if db_path.startswith("./"):
                    db_path = db_path[2:]
                
                # Convert to an absolute path using the project root, if it's not already absolute.
                # An absolute path starts with '/' (Linux/Mac) or a drive letter (Windows).
                if not (db_path.startswith("/") or (len(db_path) > 1 and db_path[1] == ":")):
                    db_path = str(project_root / db_path)
                else:
                    # If already absolute or outside the project root, the path is left unchanged.
                    pass
                
                # Ensure that the target directory for the SQLite file exists.
                db_file = Path(db_path)
                db_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Update the URL with the normalized, absolute path (forward slashes are used for cross-platform compatibility).
                normalized_path = str(db_file).replace("\\", "/")
                url = f"{parts[0]}///{normalized_path}"
    # Handle SQLite async -> sync conversion
    if "+aiosqlite" in url:
        url = url.replace("+aiosqlite", "").replace("aiosqlite", "pysqlite")
    elif "aiosqlite" in url:
        url = url.replace("aiosqlite", "pysqlite")
    
    # Handle PostgreSQL async -> sync conversion
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "").replace("asyncpg", "psycopg2")
    
    return url

# Set the SQLAlchemy URL
config.set_main_option("sqlalchemy.url", get_sync_database_url())

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This generates SQL scripts without connecting to the database.
    Useful for reviewing changes before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    Connects to the database and applies migrations directly.
    Uses a synchronous engine (Alembic requirement for SQLite).
    """
    # Create a synchronous engine for migrations
    # Alembic requires sync engine even if your app uses async
    sync_url = get_sync_database_url()
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
