"""Shared fixtures: a fresh in-memory sqlite DB per test, wired into the app."""

import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from src.db.database import Base
from src.db.deps import get_db
from src.db.models import (
    CurrencyRate,
    Group,
    GroupMember,
    Payment,
    Split,
    Template,
    User,
)
from src.main import app


@pytest_asyncio.fixture
async def db_session(monkeypatch):
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    # currency_service opens its own sessions instead of using get_db
    monkeypatch.setattr(
        "src.services.currency_service.async_session_maker", session_maker
    )
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session):
    async def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


async def _save(session, obj):
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest_asyncio.fixture
async def test_user(db_session):
    return await _save(
        db_session,
        User(api_key=str(uuid.uuid4()), name="Test User", email="test@example.com"),
    )


@pytest_asyncio.fixture
async def test_group(db_session, test_user):
    return await _save(db_session, Group(name="Test Group", owner_id=test_user.id))


@pytest_asyncio.fixture
async def test_group_member(db_session, test_group, test_user):
    return await _save(
        db_session, GroupMember(group_id=test_group.id, user_id=test_user.id)
    )


@pytest_asyncio.fixture
async def test_currency_rate(db_session):
    return await _save(
        db_session,
        CurrencyRate(
            from_currency="USD",
            to_currency="EUR",
            rate=0.85,
            updated_at=datetime.utcnow(),
        ),
    )


@pytest_asyncio.fixture
async def test_split(db_session, test_group, test_user):
    return await _save(
        db_session,
        Split(
            group_id=test_group.id,
            owner_id=test_user.id,
            receipt_data={"items": [{"name": "Pizza", "price": 20.0}], "total": 38.0},
            split_results={"Test User": 38.0},
            currency="USD",
            status="pending",
        ),
    )


@pytest_asyncio.fixture
async def test_payment(db_session, test_split):
    return await _save(
        db_session,
        Payment(
            split_id=test_split.id,
            person_name="Test User",
            amount=38.0,
            currency="USD",
            status="pending",
        ),
    )


@pytest_asyncio.fixture
async def test_template(db_session, test_user):
    return await _save(
        db_session,
        Template(
            name="Even Split Template",
            config={"type": "even", "settings": {"include_tax": True}},
            user_id=test_user.id,
        ),
    )


@pytest.fixture
def auth_headers(test_user):
    return {"X-API-Key": test_user.api_key}
