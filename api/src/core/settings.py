"""Pydantic settings for the Split Bill application.

This module provides type-safe configuration management using Pydantic Settings.
All configuration is loaded from environment variables with sensible defaults.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Settings are automatically loaded from:
    1. Environment variables
    2. .env file in the project root
    3. Default values defined below

    Attributes:
        api_key: API key for authentication
        app_base_url: Base URL for the frontend application
        fastapi_api_url: Base URL for the FastAPI backend
        openrouter_api_key: API key for OpenRouter OCR service
        openrouter_model_name: Model name for OCR processing
        openrouter_api_base_url: Base URL for OpenRouter API
        minio_endpoint: Garage/S3 endpoint address
        minio_access_key: Garage access key
        minio_secret_key: Garage secret key
        minio_bucket_name: Garage bucket name for storing receipts
        minio_use_ssl: Whether to use SSL for Garage connections
        redis_url: Redis connection URL
        debug: Enable debug mode
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    # API Configuration
    api_key: str = Field(..., description="API key for authentication")

    # Application URLs
    app_base_url: str = Field(
        default="http://localhost:15173",
        description="Base URL for the frontend application",
    )
    fastapi_api_url: str = Field(
        default="http://localhost:18000",
        description="Base URL for the FastAPI backend",
    )

    # OpenRouter Configuration
    openrouter_api_key: str = Field(
        ...,
        description="API key for OpenRouter OCR service",
    )
    openrouter_model_name: str = Field(
        default="mistralai/mistral-small-3.2-24b-instruct:free",
        description="Model name for OCR processing",
    )
    openrouter_api_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API",
    )

    # Garage/S3 Configuration
    minio_endpoint: str = Field(
        ...,
        description="Garage/S3 endpoint address (host:port)",
    )
    minio_access_key: str = Field(
        ...,
        description="Garage access key",
    )
    minio_secret_key: str = Field(
        ...,
        description="Garage secret key",
    )
    minio_bucket_name: str = Field(
        default="split-bill",
        description="Garage bucket name for storing receipts and metadata",
    )
    minio_use_ssl: bool = Field(
        default=False,
        description="Whether to use SSL for Garage connections",
    )

    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:16379",
        description="Redis connection URL with optional credentials",
    )

    # Feature Flags
    debug: bool = Field(
        default=False,
        description="Enable debug mode for development",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        json_schema_extra={"choices": ["DEBUG", "INFO", "WARNING", "ERROR"]},
    )

    # Rate Limiting
    rate_limit_upload: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Upload endpoint rate limit (requests per minute)",
    )
    rate_limit_calculate: int = Field(
        default=30,
        ge=1,
        le=500,
        description="Calculate endpoint rate limit (requests per minute)",
    )
    rate_limit_view: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="View endpoint rate limit (requests per minute)",
    )

    # File Upload Limits
    max_upload_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum upload size in megabytes",
    )

    # OCR Settings
    ocr_timeout_seconds: int = Field(
        default=60,
        ge=10,
        le=300,
        description="OCR request timeout in seconds",
    )
    ocr_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum OCR retry attempts",
    )

    # Cache TTL Settings (in seconds)
    cache_ttl_split_result: int = Field(
        default=3600,
        ge=60,
        description="Cache TTL for split results (1 hour)",
    )
    cache_ttl_ocr_result: int = Field(
        default=1800,
        ge=300,
        description="Cache TTL for OCR results (30 minutes)",
    )
    cache_ttl_share_data: int = Field(
        default=86400,
        ge=3600,
        description="Cache TTL for share data (24 hours)",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("minio_endpoint")
    @classmethod
    def validate_minio_endpoint(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError(
                f"Invalid Garage endpoint: {v}. Must be in format 'host:port'"
            )
        return v

    @property
    def minio_host(self) -> str:
        """Extract host from Garage endpoint."""
        return self.minio_endpoint.split(":")[0]

    @property
    def minio_port(self) -> int:
        """Extract port from Garage endpoint."""
        parts = self.minio_endpoint.split(":")
        return int(parts[1]) if len(parts) > 1 else 3900

    def get_cache_ttl_hours(self, key: str) -> int:
        """Get cache TTL in hours for a specific key type.

        Args:
            key: Cache key type (split_result, ocr_result, share_data)

        Returns:
            TTL in hours
        """
        ttl_map = {
            "split_result": self.cache_ttl_split_result,
            "ocr_result": self.cache_ttl_ocr_result,
            "share_data": self.cache_ttl_share_data,
        }
        return ttl_map.get(key, self.cache_ttl_split_result)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    This function returns a singleton Settings instance that is cached
    using lru_cache for performance. Settings are validated on first access.

    Returns:
        Settings: Application configuration

    Example:
        >>> settings = get_settings()
        >>> print(settings.api_key)
        ***...
    """
    return Settings()


def reload_settings() -> Settings:
    """Reload settings from environment variables.

    Use this function to refresh settings without restarting the application.
    Note: This will create a new Settings instance, breaking any cached references.

    Returns:
        Settings: Fresh application configuration
    """
    get_settings.cache_clear()
    return get_settings()
