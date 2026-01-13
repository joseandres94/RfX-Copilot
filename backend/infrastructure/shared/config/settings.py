from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from ...shared.persistence.db_adapters.sql_db_factory import DatabaseType

ENV_PATH = Path(__file__).resolve().parents[4] / ".env"

class LLMSettings(BaseSettings):
    """Settings for the infrastructure layer"""
    openai_api_key: str | None = Field(validation_alias="OPENAI_API_KEY", default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-5-mini-2025-08-07", description="Default model for agents")
    openai_model_stt: str = Field(default="gpt-4o-transcribe", description="Default model for STT tasks")
    openai_model_tts: str = Field(default="gpt-4o-mini-tts", description="Default model for TTS tasks")
    openai_model_embedding: str = Field(default="text-embedding-3-small", description="Default model for embeddings")

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        case_sensitive=False,
        extra="ignore",
    )


class DatabaseSettings(BaseSettings):
    """Settings for the database layer"""
    database_type: DatabaseType = Field(
        default="postgresql", description="Database type"
    )

    database_url: str = Field(
        default="postgresql+asyncpg://app_user:app_pass@localhost:5432/app_db",
        description="Database connection URL"
    )

    # Connection pool settings (PostgreSQL only)
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Maximum connection pool overflow")

    # Database settings
    echo_sql: bool = Field(default=False, description="Enable SQL query logging")

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        case_sensitive=False,
        extra="ignore", # Ignore extra fields from .env
    )


class AppSettings(BaseSettings):
    """Main application settings."""

    # Database settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # LLM settings
    llm: LLMSettings = Field(default_factory=LLMSettings)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore", # Ignore extra fields from .env
    )


@lru_cache
def get_settings() -> AppSettings:
    """Get cached application settings."""
    return AppSettings()