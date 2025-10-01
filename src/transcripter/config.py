"""Configuration management for Transcripter."""

import contextvars
import uuid
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TranscripterConfig(BaseSettings):
    """Application configuration with environment variable support."""

    # AssemblyAI Configuration
    assemblyai_api_key: str = Field(default="", description="AssemblyAI API key")

    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    output_dir: Path = Field(default=Path("./data/output"), description="Output directory for transcripts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=300, description="Request timeout in seconds")

    model_config = SettingsConfigDict(
        env_prefix="TRANSCRIPTER_",
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def model_post_init(self, __context) -> None:
        """Post-initialization setup."""
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Correlation ID context for logging
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id')


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one."""
    try:
        cid = correlation_id.get()
        if not cid:
            cid = generate_correlation_id()
            correlation_id.set(cid)
        return cid
    except LookupError:
        cid = generate_correlation_id()
        correlation_id.set(cid)
        return cid


def set_correlation_id(cid: str) -> None:
    """Set the correlation ID in the current context."""
    correlation_id.set(cid)


@lru_cache
def get_config() -> TranscripterConfig:
    """Get cached application configuration."""
    return TranscripterConfig()
