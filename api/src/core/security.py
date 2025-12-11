"""
Security utilities for authentication and authorization.
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for bearer tokens
security_scheme = HTTPBearer()

# Rate limiter for API endpoints
limiter = Limiter(key_func=get_remote_address)


class TokenData(BaseModel):
    """JWT token payload data."""

    user_id: Optional[str] = None
    username: Optional[str] = None
    permissions: List[str] = []
    expires_at: datetime


class User(BaseModel):
    """User model for authentication."""

    user_id: str
    username: str
    email: Optional[str] = None
    is_active: bool = True
    permissions: List[str] = []
    created_at: datetime = datetime.utcnow()


class SecurityManager:
    """Manages security operations including API key validation and JWT handling."""

    def __init__(self):
        self.api_key = settings.API_KEY
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = 30

        # JWT token settings
        self.jwt_settings = {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
        }

    def verify_api_key(self, credentials: HTTPAuthorizationCredentials) -> str:
        """
        Verify the provided API key.

        Args:
            credentials: HTTP authorization credentials

        Returns:
            The verified API key

        Raises:
            HTTPException: If the API key is invalid
        """
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if credentials.credentials != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return credentials.credentials

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token.

        Args:
            data: Data to encode in the token

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If the token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            token_type_claim = payload.get("type")
            if token_type_claim != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}, got {token_type_claim}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if token is expired
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def create_secure_hash(self, data: str) -> str:
        """
        Create a secure hash of data.

        Args:
            data: Data to hash

        Returns:
            SHA-256 hash
        """
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_secure_hash(self, data: str, hash_value: str) -> bool:
        """
        Verify data against a secure hash.

        Args:
            data: Data to verify
            hash_value: Hash to verify against

        Returns:
            True if hash matches, False otherwise
        """
        return hmac.compare_digest(self.create_secure_hash(data), hash_value)

    def create_user_token(self, user: User) -> Dict[str, Any]:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            Dictionary containing access_token and refresh_token
        """
        token_data = {
            "user_id": user.user_id,
            "username": user.username,
            "permissions": user.permissions,
        }

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
        }


# Global security manager instance
security_manager = SecurityManager()


# Rate limiting decorators
def rate_limit_upload():
    """Rate limit decorator for upload endpoints."""
    return limiter.limit("10/minute")


def rate_limit_calculate():
    """Rate limit decorator for calculate endpoints."""
    return limiter.limit("30/minute")


def rate_limit_view():
    """Rate limit decorator for view endpoints."""
    return limiter.limit("100/minute")


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    Dependency function to get and verify API key.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Verified API key

    Raises:
        HTTPException: If the API key is invalid
    """
    return security_manager.verify_api_key(credentials)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> User:
    """
    Dependency function to get and verify current user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Current user object

    Raises:
        HTTPException: If the token is invalid
    """
    token = credentials.credentials
    payload = security_manager.verify_token(token)

    user_id = payload.get("user_id")
    username = payload.get("username")

    if user_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create user object from token payload
    user = User(
        user_id=user_id,
        username=username,
        permissions=payload.get("permissions", []),
    )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency function to get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Current active user

    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> Dict[str, Any]:
    """
    Dependency function to get and verify current JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If the token is invalid
    """
    token = credentials.credentials
    return security_manager.verify_token(token)
