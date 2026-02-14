"""Tests for core settings module."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.core.settings import Settings, get_settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_with_valid_values(self):
        """Test creating settings with valid values."""
        settings = Settings(
            api_key="test-api-key",
            openrouter_api_key="test-openrouter-key",
            minio_endpoint="localhost:9000",
            minio_access_key="test-access",
            minio_secret_key="test-secret",
        )
        
        assert settings.api_key == "test-api-key"
        assert settings.openrouter_api_key == "test-openrouter-key"
        assert settings.minio_endpoint == "localhost:9000"
        assert settings.minio_bucket_name == "split-bill"
        assert settings.minio_use_ssl is False

    def test_settings_with_defaults(self):
        """Test that default values are applied."""
        settings = Settings(
            api_key="test-key",
            openrouter_api_key="test-key",
            minio_endpoint="localhost:9000",
            minio_access_key="test",
            minio_secret_key="test",
        )
        
        assert settings.app_base_url == "http://localhost:15173"
        assert settings.fastapi_api_url == "http://localhost:18000"
        assert settings.openrouter_model_name == "mistralai/mistral-small-3.2-24b-instruct:free"
        assert settings.openrouter_api_base_url == "https://openrouter.ai/api/v1"
        assert settings.redis_url == "redis://localhost:16379"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_settings_with_custom_values(self):
        """Test creating settings with custom values."""
        settings = Settings(
            api_key="test-key",
            openrouter_api_key="test-key",
            minio_endpoint="localhost:9000",
            minio_access_key="test",
            minio_secret_key="test",
            app_base_url="https://example.com",
            debug=True,
            log_level="DEBUG",
        )
        
        assert settings.app_base_url == "https://example.com"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_settings_validation_missing_required(self):
        """Test that validation fails for missing required fields."""
        with pytest.raises(ValidationError):
            Settings()  # Missing all required fields

    def test_settings_validation_invalid_endpoint(self):
        """Test endpoint validation."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                api_key="test",
                openrouter_api_key="test",
                minio_endpoint="invalid-endpoint",  # Missing port
                minio_access_key="test",
                minio_secret_key="test",
            )
        
        assert "Invalid Garage endpoint" in str(exc_info.value)

    def test_minio_host_property(self):
        """Test minio_host property extracts host."""
        settings = Settings(
            api_key="test",
            openrouter_api_key="test",
            minio_endpoint="localhost:9000",
            minio_access_key="test",
            minio_secret_key="test",
        )
        
        assert settings.minio_host == "localhost"

    def test_minio_port_property(self):
        """Test minio_port property extracts port."""
        settings = Settings(
            api_key="test",
            openrouter_api_key="test",
            minio_endpoint="localhost:9000",
            minio_access_key="test",
            minio_secret_key="test",
        )
        
        assert settings.minio_port == 9000

    def test_minio_port_property_default(self):
        """Test minio_port property with default port."""
        settings = Settings(
            api_key="test",
            openrouter_api_key="test",
            minio_endpoint="localhost",  # No port specified
            minio_access_key="test",
            minio_secret_key="test",
        )
        
        assert settings.minio_port == 3900  # Default port

    @patch.dict(os.environ, {
        "API_KEY": "env-api-key",
        "OPENROUTER_API_KEY": "env-openrouter-key",
        "MINIO_ENDPOINT": "env-host:9000",
        "MINIO_ACCESS_KEY": "env-access",
        "MINIO_SECRET_KEY": "env-secret",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
    }, clear=True)
    def test_settings_from_environment(self):
        """Test loading settings from environment variables."""
        settings = Settings()
        
        assert settings.api_key == "env-api-key"
        assert settings.openrouter_api_key == "env-openrouter-key"
        assert settings.minio_endpoint == "env-host:9000"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_minio_use_ssl_from_string(self):
        """Test that minio_use_ssl handles string values."""
        with patch.dict(os.environ, {"MINIO_USE_SSL": "true"}, clear=False):
            settings = Settings(
                api_key="test",
                openrouter_api_key="test",
                minio_endpoint="localhost:9000",
                minio_access_key="test",
                minio_secret_key="test",
            )
            # Note: Pydantic should handle boolean conversion
            assert isinstance(settings.minio_use_ssl, bool)


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test that get_settings returns a Settings instance."""
        with patch.dict(os.environ, {
            "API_KEY": "test",
            "OPENROUTER_API_KEY": "test",
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "test",
            "MINIO_SECRET_KEY": "test",
        }, clear=True):
            settings = get_settings()
            assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self):
        """Test that get_settings uses lru_cache."""
        with patch.dict(os.environ, {
            "API_KEY": "test",
            "OPENROUTER_API_KEY": "test",
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "test",
            "MINIO_SECRET_KEY": "test",
        }, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()
            # Should be the same object due to lru_cache
            assert settings1 is settings2
