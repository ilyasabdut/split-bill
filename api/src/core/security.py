"""
Security utilities for authentication and authorization.
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for bearer tokens
security_scheme = HTTPBearer()


class SecurityManager:
    """Manages security operations including API key validation and JWT handling."""

    def __init__(self):
        self.api_key = settings.API_KEY
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

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

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If the token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
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


# Global security manager instance
security_manager = SecurityManager()


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
