"""
Unit tests
for core.security module.
Tests security utilities and authentication.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from src.core.security import (
    TokenData,
    User,
    SecurityManager,
    security_manager,
    rate_limit_upload,
    rate_limit_calculate,
    rate_limit_view,
    get_api_key,
    get_current_user,
    get_current_active_user,
    get_current_token,
)


class TestTokenData:
    """Test TokenData model."""

    def test_token_data_creation(self):
        """Test TokenData creation."""
        token_data = TokenData(
            user_id="123",
            username="testuser",
            permissions=["read", "write"],
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        assert token_data.user_id == "123"
        assert token_data.username == "testuser"
        assert token_data.permissions == ["read", "write"]

    def test_token_data_defaults(self):
        """Test TokenData with default values."""
        token_data = TokenData(
            user_id="123",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        assert token_data.username is None
        assert token_data.permissions == []


class TestUser:
    """Test User model."""

    def test_user_creation(self):
        """Test User creation."""
        user = User(
            user_id="123",
            username="testuser",
            email="test@example.com",
            is_active=True,
            permissions=["read", "write"],
            created_at=datetime.utcnow(),
        )

        assert user.user_id == "123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.permissions == ["read", "write"]

    def test_user_defaults(self):
        """Test User with default values."""
        user = User(
            user_id="123",
            username="testuser",
        )

        assert user.email is None
        assert user.is_active is True
        assert user.permissions == []
        assert isinstance(user.created_at, datetime)


class TestSecurityManagerInitialization:
    """Test SecurityManager initialization."""

    def test_security_manager_initialization(self):
        """Test SecurityManager initialization."""
        manager = SecurityManager()
        assert manager.api_key is not None
        assert manager.secret_key is not None
        assert manager.algorithm == "HS256"
        assert manager.access_token_expire_minutes > 0
        assert manager.refresh_token_expire_days > 0

    def test_security_manager_jwt_settings(self):
        """Test SecurityManager JWT settings."""
        manager = SecurityManager()
        assert "secret_key" in manager.jwt_settings
        assert "algorithm" in manager.jwt_settings
        assert "access_token_expire_minutes" in manager.jwt_settings
        assert "refresh_token_expire_days" in manager.jwt_settings


class TestSecurityManagerVerifyApiKey:
    """Test SecurityManager verify_api_key method."""

    def test_verify_api_key_success(self):
        """Test successful API key verification."""
        manager = SecurityManager()
        credentials = MagicMock()
        credentials.scheme = "Bearer"
        credentials.credentials = manager.api_key

        result = manager.verify_api_key(credentials)
        assert result == manager.api_key

    def test_verify_api_key_invalid_scheme(self):
        """Test API key verification with invalid scheme."""
        manager = SecurityManager()
        credentials = MagicMock()
        credentials.scheme = "Basic"
        credentials.credentials = manager.api_key

        with pytest.raises(HTTPException) as exc_info:
            manager.verify_api_key(credentials)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_api_key_invalid_key(self):
        """Test API key verification with invalid key."""
        manager = SecurityManager()
        credentials = MagicMock()
        credentials.scheme = "Bearer"
        credentials.credentials = "invalid-key"

        with pytest.raises(HTTPException) as exc_info:
            manager.verify_api_key(credentials)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestSecurityManagerCreateAccessToken:
    """Test SecurityManager create_access_token method."""

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}

        token = manager.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        expire = timedelta(minutes=30)

        token = manager.create_access_token(data, expires_delta=expire)
        assert isinstance(token, str)
        assert len(token) > 0


class TestSecurityManagerCreateRefreshToken:
    """Test SecurityManager create_refresh_token method."""

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}

        token = manager.create_refresh_token(data)
        assert isinstance(token, str)
        assert len(token) > 0


class TestSecurityManagerVerifyToken:
    """Test SecurityManager verify_token method."""

    def test_verify_access_token_success(self):
        """Test successful access token verification."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        token = manager.create_access_token(data)

        payload = manager.verify_token(token, token_type="access")
        assert payload["user_id"] == "123"
        assert payload["username"] == "testuser"

    def test_verify_refresh_token_success(self):
        """Test successful refresh token verification."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        token = manager.create_refresh_token(data)

        payload = manager.verify_token(token, token_type="refresh")
        assert payload["user_id"] == "123"
        assert payload["username"] == "testuser"

    def test_verify_token_invalid_type(self):
        """Test token verification with invalid type."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        token = manager.create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            manager.verify_token(token, token_type="refresh")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_token_expired(self):
        """Test expired token verification."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        # Create token with very short expiry
        token = manager.create_access_token(data, expires_delta=timedelta(seconds=-1))

        with pytest.raises(HTTPException) as exc_info:
            manager.verify_token(token, token_type="access")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestSecurityManagerPasswordHashing:
    """Test SecurityManager password hashing methods."""

    def test_hash_password(self):
        """Test password hashing."""
        manager = SecurityManager()
        password = "testpassword123"
        hashed = manager.hash_password(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_success(self):
        """Test successful password verification."""
        manager = SecurityManager()
        password = "testpassword123"
        hashed = manager.hash_password(password)

        result = manager.verify_password(password, hashed)
        assert result is True

    def test_verify_password_failure(self):
        """Test failed password verification."""
        manager = SecurityManager()
        password = "testpassword123"
        hashed = manager.hash_password(password)

        result = manager.verify_password("wrongpassword", hashed)
        assert result is False


class TestSecurityManagerSecureHash:
    """Test SecurityManager secure hash methods."""

    def test_create_secure_hash(self):
        """Test creating secure hash."""
        manager = SecurityManager()
        data = "test data to hash"
        hash_value = manager.create_secure_hash(data)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA-256 produces 64 hex characters

    def test_verify_secure_hash_success(self):
        """Test successful secure hash verification."""
        manager = SecurityManager()
        data = "test data to hash"
        hash_value = manager.create_secure_hash(data)

        result = manager.verify_secure_hash(data, hash_value)
        assert result is True

    def test_verify_secure_hash_failure(self):
        """Test failed secure hash verification."""
        manager = SecurityManager()
        data = "test data to hash"
        hash_value = manager.create_secure_hash(data)

        result = manager.verify_secure_hash("wrong data", hash_value)
        assert result is False


class TestSecurityManagerCreateUserToken:
    """Test SecurityManager create_user_token method."""

    def test_create_user_token(self):
        """Test creating user tokens."""
        manager = SecurityManager()
        user = User(
            user_id="123",
            username="testuser",
            permissions=["read", "write"],
        )

        tokens = manager.create_user_token(user)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens
        assert tokens["token_type"] == "bearer"


class TestRateLimitDecorators:
    """Test rate limiting decorators."""

    def test_rate_limit_upload(self):
        """Test rate_limit_upload decorator."""
        decorator = rate_limit_upload()
        assert decorator is not None

    def test_rate_limit_calculate(self):
        """Test rate_limit_calculate decorator."""
        decorator = rate_limit_calculate()
        assert decorator is not None

    def test_rate_limit_view(self):
        """Test rate_limit_view decorator."""
        decorator = rate_limit_view()
        assert decorator is not None


class TestGetApiKeyDependency:
    """Test get_api_key dependency."""

    def test_get_api_key_with_valid_credentials(self):
        """Test get_api_key with valid credentials."""
        manager = SecurityManager()
        credentials = MagicMock()
        credentials.scheme = "Bearer"
        credentials.credentials = manager.api_key

        result = get_api_key(credentials)
        assert result == manager.api_key


class TestGetCurrentUserDependency:
    """Test get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test get_current_user with valid token."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser", "permissions": ["read"]}
        token = manager.create_access_token(data)

        credentials = MagicMock()
        credentials.credentials = token

        user = await get_current_user(credentials)
        assert user.user_id == "123"
        assert user.username == "testuser"
        assert user.permissions == ["read"]

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token."""
        credentials = MagicMock()
        credentials.credentials = "invalid-token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentActiveUserDependency:
    """Test get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_active_user_active(self):
        """Test get_current_active_user with active user."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        token = manager.create_access_token(data)

        credentials = MagicMock()
        credentials.credentials = token

        user = await get_current_user(credentials)
        active_user = await get_current_active_user(user)
        assert active_user.user_id == "123"
        assert active_user.is_active is True

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        """Test get_current_active_user with inactive user."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        token = manager.create_access_token(data)

        credentials = MagicMock()
        credentials.credentials = token

        user = await get_current_user(credentials)
        user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(user)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetCurrentTokenDependency:
    """Test get_current_token dependency."""

    @pytest.mark.asyncio
    async def test_get_current_token_valid(self):
        """Test get_current_token with valid token."""
        manager = SecurityManager()
        data = {"user_id": "123", "username": "testuser"}
        token = manager.create_access_token(data)

        credentials = MagicMock()
        credentials.credentials = token

        payload = await get_current_token(credentials)
        assert payload["user_id"] == "123"
        assert payload["username"] == "testuser"


class TestGlobalSecurityManagerInstance:
    """Test global security_manager instance."""

    def test_global_security_manager_exists(self):
        """Test that global security_manager instance exists."""
        assert security_manager is not None
        assert isinstance(security_manager, SecurityManager)
