from typing import Literal

from .database_adapter import DatabaseAdapter
from .sqlite_adapter import SQLiteAdapter
from .postgresql_adapter import PostgreSQLAdapter

DatabaseType = Literal["postgresql", "sqlite"]

def create_database_adapter(
    database_type: DatabaseType,
    database_url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
) -> DatabaseAdapter:
    """Create a database adapter based on configuration.

    Args:
        database_type: Type of database (postgresql, sqlite)
        database_url: Database connection URL
        pool_size: Connection pool size (PostgreSQL only)
        max_overflow: Max connection pool overflow (PostgreSQL only)

    Returns:
        Configured database adapter instance

    Raises:
        ValueError: If database_type is not supported
    """
    if database_type == "postgresql":
        return PostgreSQLAdapter(
            database_url=database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
    elif database_type == "sqlite":
        return SQLiteAdapter(database_url=database_url)