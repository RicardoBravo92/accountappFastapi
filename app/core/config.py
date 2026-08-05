import logging
import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "accountapp"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./accountapp.db"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB default

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def get_database_connection_kwargs(self) -> dict:
        """Get database connection parameters with proper encoding."""
        from sqlalchemy.engine.url import make_url

        url = make_url(self.DATABASE_URL)
        kwargs = dict(url.query)

        # Add proper encoding parameters for PostgreSQL
        if self.DATABASE_URL.startswith("postgresql"):
            kwargs.setdefault("client_encoding", "utf-8")
            kwargs.setdefault("options", "-c statement_timeout=30000")

        # Add connection pool settings
        kwargs.setdefault("pool_size", 10)
        kwargs.setdefault("max_overflow", 20)
        kwargs.setdefault("pool_timeout", 30)
        kwargs.setdefault("pool_recycle", 3600)

        return kwargs


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()


# Configure logging based on environment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
