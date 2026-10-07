import logging
from functools import lru_cache

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

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

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

    def validate_production_settings(self) -> list[str]:
        """Validate settings for production environment.

        Returns a list of validation warning messages.
        """
        warnings = []

        if self.is_production:
            # Check SECRET_KEY
            if self.SECRET_KEY == "change-me-in-production" or len(self.SECRET_KEY) < 32:
                warnings.append(
                    "SECRET_KEY must be set to a secure random string of at least 32 characters in production"
                )

            # Check CORS origins don't include wildcards
            if "*" in self.CORS_ORIGINS:
                warnings.append(
                    "CORS_ORIGINS must not include wildcard '*' in production"
                )

            # Warn about SQLite in production
            if self.DATABASE_URL.startswith("sqlite"):
                warnings.append(
                    "SQLite is not recommended for production. Use PostgreSQL instead."
                )

            # Check DEBUG
            if self.DEBUG:
                warnings.append("DEBUG should be false in production")

        return warnings


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()

# Validate and log warnings on startup
_warnings = settings.validate_production_settings()
for _warning in _warnings:
    logging.warning(f"Configuration Warning: {_warning}")


# Configure logging based on environment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
