"""
Unit tests for core.config module.
Tests Settings class and environment variable loading.
"""



from src.core.config import Settings


class TestSettingsInitialization:
    """Test Settings initialization."""

    def test_default_api_key(self, monkeypatch):
        """Test default API key value."""
        monkeypatch.delenv("API_KEY", raising=False)
        settings = Settings()
        assert settings.API_KEY == "your-api-key-here"

    def test_custom_api_key(self, monkeypatch):
        """Test custom API key from environment."""
        monkeypatch.setenv("API_KEY", "custom-api-key")
        settings = Settings()
        assert settings.API_KEY == "custom-api-key"

    def test_default_app_base_url(self, monkeypatch):
        """Test default APP_BASE_URL value."""
        monkeypatch.delenv("APP_BASE_URL", raising=False)
        settings = Settings()
        assert settings.APP_BASE_URL == "http://localhost:8000"

    def test_custom_app_base_url(self, monkeypatch):
        """Test custom APP_BASE_URL from environment."""
        monkeypatch.setenv("APP_BASE_URL", "https://api.example.com")
        settings = Settings()
        assert settings.APP_BASE_URL == "https://api.example.com"


class TestOpenRouterSettings:
    """Test OpenRouter configuration settings."""

    def test_default_openrouter_api_key(self, monkeypatch):
        """Test default OpenRouter API key."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        settings = Settings()
        assert settings.OPENROUTER_API_KEY == "your-openrouter-key"

    def test_custom_openrouter_api_key(self, monkeypatch):
        """Test custom OpenRouter API key."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "custom-openrouter-key")
        settings = Settings()
        assert settings.OPENROUTER_API_KEY == "custom-openrouter-key"

    def test_default_openrouter_model_name(self, monkeypatch):
        """Test default OpenRouter model name."""
        monkeypatch.delenv("OPENROUTER_MODEL_NAME", raising=False)
        settings = Settings()
        assert settings.OPENROUTER_MODEL_NAME == "mistralai/mistral-small-3.2-24b-instruct:free"

    def test_custom_openrouter_model_name(self, monkeypatch):
        """Test custom OpenRouter model name."""
        monkeypatch.setenv("OPENROUTER_MODEL_NAME", "gpt-4")
        settings = Settings()
        assert settings.OPENROUTER_MODEL_NAME == "gpt-4"

    def test_default_openrouter_api_base_url(self, monkeypatch):
        """Test default OpenRouter API base URL."""
        monkeypatch.delenv("OPENROUTER_API_BASE_URL", raising=False)
        settings = Settings()
        assert settings.OPENROUTER_API_BASE_URL == "https://openrouter.ai/api/v1"

    def test_custom_openrouter_api_base_url(self, monkeypatch):
        """Test custom OpenRouter API base URL."""
        monkeypatch.setenv("OPENROUTER_API_BASE_URL", "https://custom.openrouter.ai/api/v1")
        settings = Settings()
        assert settings.OPENROUTER_API_BASE_URL == "https://custom.openrouter.ai/api/v1"

    def test_default_openrouter_http_referer(self, monkeypatch):
        """Test default OpenRouter HTTP referer."""
        monkeypatch.delenv("OPENROUTER_HTTP_REFERER", raising=False)
        settings = Settings()
        assert settings.OPENROUTER_HTTP_REFERER is None

    def test_custom_openrouter_http_referer(self, monkeypatch):
        """Test custom OpenRouter HTTP referer."""
        monkeypatch.setenv("OPENROUTER_HTTP_REFERER", "https://example.com")
        settings = Settings()
        assert settings.OPENROUTER_HTTP_REFERER == "https://example.com"

    def test_default_openrouter_x_title(self, monkeypatch):
        """Test default OpenRouter X-Title."""
        monkeypatch.delenv("OPENROUTER_X_TITLE", raising=False)
        settings = Settings()
        assert settings.OPENROUTER_X_TITLE is None

    def test_custom_openrouter_x_title(self, monkeypatch):
        """Test custom OpenRouter X-Title."""
        monkeypatch.setenv("OPENROUTER_X_TITLE", "My App")
        settings = Settings()
        assert settings.OPENROUTER_X_TITLE == "My App"


class TestMinIOSettings:
    """Test MinIO configuration settings."""

    def test_default_minio_endpoint(self, monkeypatch):
        """Test default MinIO endpoint."""
        monkeypatch.delenv("MINIO_ENDPOINT", raising=False)
        settings = Settings()
        assert settings.MINIO_ENDPOINT == "localhost:9000"

    def test_custom_minio_endpoint(self, monkeypatch):
        """Test custom MinIO endpoint."""
        monkeypatch.setenv("MINIO_ENDPOINT", "minio.example.com:9000")
        settings = Settings()
        assert settings.MINIO_ENDPOINT == "minio.example.com:9000"

    def test_default_minio_access_key(self, monkeypatch):
        """Test default MinIO access key."""
        monkeypatch.delenv("MINIO_ACCESS_KEY", raising=False)
        settings = Settings()
        assert settings.MINIO_ACCESS_KEY == "minioadmin"

    def test_custom_minio_access_key(self, monkeypatch):
        """Test custom MinIO access key."""
        monkeypatch.setenv("MINIO_ACCESS_KEY", "custom-access-key")
        settings = Settings()
        assert settings.MINIO_ACCESS_KEY == "custom-access-key"

    def test_default_minio_secret_key(self, monkeypatch):
        """Test default MinIO secret key."""
        monkeypatch.delenv("MINIO_SECRET_KEY", raising=False)
        settings = Settings()
        assert settings.MINIO_SECRET_KEY == "minioadmin"

    def test_custom_minio_secret_key(self, monkeypatch):
        """Test custom MinIO secret key."""
        monkeypatch.setenv("MINIO_SECRET_KEY", "custom-secret-key")
        settings = Settings()
        assert settings.MINIO_SECRET_KEY == "custom-secret-key"

    def test_default_minio_bucket_name(self, monkeypatch):
        """Test default MinIO bucket name."""
        monkeypatch.delenv("MINIO_BUCKET_NAME", raising=False)
        settings = Settings()
        assert settings.MINIO_BUCKET_NAME == "split-bill"

    def test_custom_minio_bucket_name(self, monkeypatch):
        """Test custom MinIO bucket name."""
        monkeypatch.setenv("MINIO_BUCKET_NAME", "custom-bucket")
        settings = Settings()
        assert settings.MINIO_BUCKET_NAME == "custom-bucket"

    def test_default_minio_use_ssl_false(self, monkeypatch):
        """Test default MinIO SSL setting (False)."""
        monkeypatch.delenv("MINIO_USE_SSL", raising=False)
        settings = Settings()
        assert settings.MINIO_USE_SSL is False

    def test_minio_use_ssl_true(self, monkeypatch):
        """Test MinIO SSL setting (True)."""
        monkeypatch.setenv("MINIO_USE_SSL", "true")
        settings = Settings()
        assert settings.MINIO_USE_SSL is True

    def test_minio_use_ssl_false_string(self, monkeypatch):
        """Test MinIO SSL setting (false string)."""
        monkeypatch.setenv("MINIO_USE_SSL", "false")
        settings = Settings()
        assert settings.MINIO_USE_SSL is False

    def test_minio_use_ssl_case_insensitive(self, monkeypatch):
        """Test MinIO SSL setting case insensitivity."""
        monkeypatch.setenv("MINIO_USE_SSL", "True")
        settings = Settings()
        assert settings.MINIO_USE_SSL is True


class TestDatabaseSettings:
    """Test database configuration settings."""

    def test_default_database_url(self, monkeypatch):
        """Test default database URL."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        settings = Settings()
        assert settings.DATABASE_URL == "postgresql+asyncpg://user:password@localhost:5432/splitbill"

    def test_custom_database_url(self, monkeypatch):
        """Test custom database URL."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
        settings = Settings()
        assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db"


class TestRedisSettings:
    """Test Redis configuration settings."""

    def test_default_redis_url(self, monkeypatch):
        """Test default Redis URL."""
        monkeypatch.delenv("REDIS_URL", raising=False)
        settings = Settings()
        assert settings.REDIS_URL == "redis://localhost:6379"

    def test_custom_redis_url(self, monkeypatch):
        """Test custom Redis URL."""
        monkeypatch.setenv("REDIS_URL", "redis://redis.example.com:6380")
        settings = Settings()
        assert settings.REDIS_URL == "redis://redis.example.com:6380"


class TestSecuritySettings:
    """Test security configuration settings."""

    def test_default_secret_key(self, monkeypatch):
        """Test default secret key."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        settings = Settings()
        assert settings.SECRET_KEY == "your-secret-key-here"

    def test_custom_secret_key(self, monkeypatch):
        """Test custom secret key."""
        monkeypatch.setenv("SECRET_KEY", "custom-secret-key")
        settings = Settings()
        assert settings.SECRET_KEY == "custom-secret-key"

    def test_default_access_token_expire_minutes(self, monkeypatch):
        """Test default access token expiration."""
        monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
        settings = Settings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_custom_access_token_expire_minutes(self, monkeypatch):
        """Test custom access token expiration."""
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        settings = Settings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60


class TestRateLimitSettings:
    """Test rate limiting configuration settings."""

    def test_default_rate_limit_per_minute(self, monkeypatch):
        """Test default rate limit."""
        monkeypatch.delenv("RATE_LIMIT_PER_MINUTE", raising=False)
        settings = Settings()
        assert settings.RATE_LIMIT_PER_MINUTE == 60

    def test_custom_rate_limit_per_minute(self, monkeypatch):
        """Test custom rate limit."""
        monkeypatchkt.setenv("RATE_LIMIT_PER_MINUTE", "120")
        settings = Settings()
        assert settings.RATE_LIMIT_PER_MINUTE == 120


class TestLoggingSettings:
    """Test logging configuration settings."""

    def test_default_log_level(self, monkeypatch):
        """Test default log level."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        settings = Settings()
        assert settings.LOG_LEVEL == "INFO"

    def test_custom_log_level(self, monkeypatch):
        """Test custom log level."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.LOG_LEVEL == "DEBUG"

    def test_default_log_format(self, monkeypatch):
        """Test default log format."""
        monkeypatch.delenv("LOG_FORMAT", raising=False)
        settings = Settings()
        assert "%(asctime)s" in settings.LOG_FORMAT
        assert "%(name)s" in settings.LOG_FORMAT
        assert "%(levelname)s" in settings.LOG_FORMAT
        assert "%(message)s" in settings.LOG_FORMAT

    def test_custom_log_format(self, monkeypatch):
        """Test custom log format."""
        custom_format = "%(asctime)s - %(message)s"
        monkeypatch.setenv("LOG_FORMAT", custom_format)
        settings = Settings()
        assert settings.LOG_FORMAT == custom_format


class TestImageProcessingSettings:
    """Test image processing configuration settings."""

    def test_default_max_image_size_mb(self, monkeypatch):
        """Test default max image size in MB."""
        monkeypatch.delenv("MAX_IMAGE_SIZE_MB", rasing=False)
        settings = Settings()
        assert settings.MAX_IMAGE_SIZE_MB == 2

    def test_custom_max_image_size_mb(self, monkeypatch):
        """Test custom max image size in MB."""
        monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "5")
        settings = Settings()
        assert settings.MAX_IMAGE_SIZE_MB == 5

    def test_max_image_size_bytes_calculation(self, monkeypatch):
        """Test max image size in bytes calculation."""
        monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "2")
        settings = Settings()
        expected_bytes = 2 * 1024 * 1024
        assert settings.MAX_IMAGE_SIZE_BYTES == expected_bytes

    def test_max_image_size_bytes_custom_mb(self, monkeypatch):
        """Test max image size in bytes with custom MB."""
        monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "10")
        settings = Settings()
        expected_bytes = 10 * 1024 * 1024
        assert settings.MAX_IMAGE_SIZE_BYTES == expected_bytes


class TestGlobalSettingsInstance:
    """Test global settings instance."""

    def test_global_settings_instance(self, monkeypatch):
        """Test that global settings instance exists."""
        from src.core.config import settings
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_global_settings_uses_env_vars(self, monkeypatch):
        """Test that global settings uses environment variables."""
        monkeypatch.setenv("API_KEY", "global-test-key")
        # Re-import to get fresh instance
        import importlib
        importlib.reload(__import__("src.core.config"))
        from src.core.config import settings
        assert settings.API_KEY == "global-test-key"
