import os
import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session_maker
from .models import User

# auto_error=False so a missing header is a 401 like a wrong one, not a 403
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Verify API key from Bearer token."""
    # read at call time: main.py loads .env after this module is imported
    api_key = os.environ.get("API_KEY", "default-dev-key-123")
    if credentials is None or credentials.credentials != api_key:
        raise _unauthorized("Invalid or missing API Key")
    return credentials.credentials


async def _user_for_device(db: AsyncSession, device_id: str) -> User:
    user = await db.scalar(select(User).where(User.device_id == device_id))
    if user is not None:
        return user
    # api_key is a legacy NOT NULL column nothing reads; fill it with noise
    user = User(device_id=device_id, api_key=uuid.uuid4().hex, name="You")
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        # another first request from the same device won the insert
        await db.rollback()
        return await db.scalar(select(User).where(User.device_id == device_id))
    await db.refresh(user)
    return user


def _parse_device_id(value: str) -> str:
    try:
        return str(uuid.UUID(value))
    except ValueError:
        raise _unauthorized("Invalid X-Device-Id")


# ponytail: identity is one anonymous id per browser (localStorage); clearing
# storage or switching device loses it. Upgrade path: real login that links
# device ids to an account.
async def get_current_user(
    _: str = Depends(get_api_key),
    x_device_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not x_device_id:
        raise _unauthorized("Missing X-Device-Id")
    return await _user_for_device(db, _parse_device_id(x_device_id))


async def get_optional_user(
    x_device_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Same identity, but anonymous callers are allowed (splits)."""
    if not x_device_id:
        return None
    return await _user_for_device(db, _parse_device_id(x_device_id))
