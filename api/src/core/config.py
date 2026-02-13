"""
Core configuration settings for the application.
"""

import os


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # API Configuration
        self.API_KEY = os.getenv("API_KEY", "your-api-key-here")
        self.APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
        self.FASTAPI_API_URL = os.getenv("FASTAPI_API_URL", "http://localhost:8000")

        # OpenRouter Configuration
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")
        self.OPENROUTER_MODEL_NAME = os.getenv(
            "OPENROUTER_MODEL_NAME", "mistralai/mistral-small-3.2-24b-instruct:free"
        )
        self.OPENROUTER_API_BASE_URL = os.getenv(
            "OPENROUTER_API_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.OPENROUTER_HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER")
        self.OPENROUTER_X_TITLE = os.getenv("OPENROUTER_X_TITLE")

        # MinIO Configuration
        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "split-bill")
        self.MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "False").lower() == "true"

        # Database Configuration
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost:5432/splitbill",
        )

        # Redis Configuration (for caching)
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Security Configuration
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Rate Limiting
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv(
            "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Image Processing
        self.MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "2"))
        self.MAX_IMAGE_SIZE_BYTES = self.MAX_IMAGE_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
