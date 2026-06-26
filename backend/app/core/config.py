"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "CodeToQuery"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database URL (required)",
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # Redis (for Celery)
    REDIS_URL: str = Field(
        ...,
        description="Redis URL (required)",
    )
    CELERY_BROKER_URL: str = Field(
        ...,
        description="Celery broker URL (required)",
    )
    CELERY_RESULT_BACKEND: str = Field(
        ...,
        description="Celery result backend URL (required)",
    )

    # Security
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token generation (min 32 chars, required)",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:8000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Analysis
    DEFAULT_COST_THRESHOLD: int = 1000
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.85
    EXPLAIN_TIMEOUT: int = 30
    ENABLE_ANALYZE: bool = False

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = ".js,.py,.ts,.go,.java"

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is not a placeholder."""
        if v in ["your-secret-key-here-change-in-production", "dev-secret-key-change-in-production", ""]:
            raise ValueError(
                "SECRET_KEY cannot be a placeholder value. "
                "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL is not a placeholder."""
        if "codetoquery:codetoquery" in v and "localhost" in v:
            raise ValueError(
                "DATABASE_URL contains default credentials. "
                "Please set secure database credentials."
            )
        return v

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v if isinstance(v, list) else [v]

    @field_validator("ALLOWED_EXTENSIONS", mode="after")
    @classmethod
    def parse_allowed_extensions(cls, v: str) -> list[str]:
        """Parse allowed extensions from comma-separated string."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v if isinstance(v, list) else [v]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.DATABASE_URL

    @property
    def database_url_async(self) -> str:
        """Get asynchronous database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
