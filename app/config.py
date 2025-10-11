"""Application configuration utilities."""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class Settings:
    """Runtime configuration values sourced from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://dev:dev@localhost:5432/vecdb"
    )
    model_name: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "384"))


_cached_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Return a cached Settings instance to avoid recomputing env lookups."""

    global _cached_settings
    if _cached_settings is None:
        _cached_settings = Settings()
    return _cached_settings
