
"""Test configuration and fixtures for the split-bill API."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Test database URL - using SQLite for simplicity
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for tests
async_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """Create all tables before tests and drop after."""
    from src.db.database import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()


@pytest_asyncio.fixture
async def db_session(set(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for each test."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(set(db_session: AsyncSession) -> Generator[None, None, None]:
    """Override the dependency to use test database."""
    from src.db.deps import get_db

    async def _get_db():
        yield db_session

    # Create test app
    from fastapi import FastAPI
    from src.routers import (
        analytics_router,
        groups_router,
        payments_router,
        templates_router,
    )

    test_app = FastAPI()
    test_app.include_router(groups_router)
    test_app.include_router(templates_router)
    test_app.include_router(payments_router)
    test_app.include_router(analytics_router)

    test_app.dependency_overrides[get_db] = _get_db
    yield
    test_app.dependency_overrides.clear()


@pytest.fixture
def test_client(override_get_db: None) -> TestClient:
    """Create a test client."""
    from fastapi import FastAPI
    from src.routers import (
        analytics_router,
        groups_router,
        payments_router,
        templates_router,
    )

    test_app = FastAPI()
    test_app.include_router(groups_router)
    test_app.include_router(templates_router)
    test_app.include_router(payments_router)
    test_app.include_router(analytics_router)

    return TestClient(test_app)


@pytest_asyncio.fixture
async def async_client(override_get_db: None) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    from fastapi import FastAPI
    from src.routers import (
        analytics_router,
        groups_router,
        payments_router,
        templates_router,
    )

    test_app = FastAPI()
    test_app.include_router(groups_router)
    test_app.include_router(templates_router)
    test_app.include_router(payments_router)
    test_app.include_router(analytics_router)

    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client


# Model Fixtures


@pytest.fixture
def user_data():
    """Sample user data."""
    return {
        "api_key": str(uuid.uuid4()),
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest_asyncio.fixture
async def test_user(set(db_session: AsyncSession, user_data: dict):
    """Create a test user."""
    from src.db.models import User
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def group_data():
    """Sample group data."""
    return {
        "name": "Test Group",
    }


@pytest_asyncio.fixture
async def test_group(set(db_session: AsyncSession, test_user, group_data: dict):
    """Create a test group owned by test user."""
    from src.db.models import Group
    group = Group(**group_data, owner_id=test_user.id)
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    return group


@pytest_asyncio.fixture
async def test_group_member(set(db_session: AsyncSession, test_group, test_user):
    """Add test user to test group."""
    from src.db.models import GroupMember
    member = GroupMember(group_id=test_group.id, user_id=test_user.id)
    db_session.add(member)
    await db_session.commit()
    return member


@pytest.fixture
def split_data():
    """Sample split data."""
    return {
        "receipt_data": {
            "items": [
                {"name": "Pizza", "price": 20.0, "quantity": 1},
                {"name": "Drinks", "price": 10.0, "quantity": 2},
            ],
            "tax": 3.0,
            "tip": 5.0,
            "total": 38.0,
        },
        "split_results": {
            "Test User": 38.0,
        },
        "currency": "USD",
        "status": "pending",
    }


@pytest_asyncio.fixture
async def test_split(set(db_session: AsyncSession, test_group, test_user, split_data: dict):
    """Create a test split."""
    from src.db.models import Split
    split = Split(
        **split_data,
        group_id=test_group.id,
        owner_id=test_user.id,
    )
    db_session.add(split)
    await db_session.commit()
    await db_session.refresh(split)
    return split


@pytest.fixture
def payment_data():
    """Sample payment data."""
    return {
        "person_name": "Test User",
        "amount": 38.0,
        "currency": "USD",
        "status": "pending",
    }


@pytest_asyncio.fixture
async def test_payment(set(db_session: AsyncSession, test_split, payment_data: dict):
    """Create a test payment."""
    from src.db.models import Payment
    payment = Payment(**payment_data, split_id=test_split.id)
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    return payment


@pytest.fixture
def template_data():
    """Sample template data."""
    return {
        "name": "Even Split Template",
        "config": {
            "type": "even",
            "settings": {
                "include_tax": True,
                "include_tip": True,
            },
        },
    }


@pytest_asyncio.fixture
async def test_template(set(db_session: AsyncSession, test_user, template_data: dict):
    """Create a test template."""
    from src.db.models import Template
    template = Template(**template_data, user_id=test_user.id)
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    return template


@pytest.fixture
def currency_rate_data():
    """Sample currency rate data."""
    return {
        "from_currency": "USD",
        "to_currency": "EUR",
        "rate": 0.85,
        "updated_at": datetime.utcnow(),
    }


@pytest_asyncio.fixture
async def test_currency_rate(set(db_session: AsyncSession, currency_rate_data: dict):
    """Create a test currency rate."""
    from src.db.models import CurrencyRate
    rate = CurrencyRate(**currency_rate_data)
    db_session.add(rate)
    await db_session.commit()
    await db_session.refresh(rate)
    return rate


# Mock Fixtures


@pytest.fixture
def mock_currency_api():
    """Mock currency API responses."""
    with patch("src.services.currency_service.aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "result": "success",
            "conversion_rates": {
                "EUR": 0.85,
                "GBP": 0.73,
                "JPY": 110.0,
            },
        }
        mock_get = AsyncMock(return_value=mock_response)
        mock_session.return_value.__aenter__.return_value.get = mock_get
        yield mock_session


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    return {"X-API-Key": test_user.api_key}


# Helper Functions


def create_test_user(set(db_session: AsyncSession, **kwargs):
    """Helper to create a user with custom data."""
    from src.db.models import User
    data = {
        "api_key": str(uuid.uuid4()),
        "name": kwargs.get("name", "Test User"),
        "email": kwargs.get("email", f"{uuid.uuid4()}@example.com"),
    }
    user = User(**data)
    db_session.add(user)
    return user


def create_test_group(set(db_session: AsyncSession) -> Group, **kwargs):
    """Helper to create a group with custom data."""
    from src.db.models import Group
    data = {
        "name": kwargs.get("name", "Test Group"),
        "owner_id": owner.id,
    }
    group = Group(**data)
    db_session.add(group)
    return group


def create_test_split(set(db_session: AsyncSession, group, owner, **kwargs):
    """Helper to create a split with custom data."""
    from src.db.models import Split
    data = {
        "group_id": group.id,
        "owner_id": owner.id,
        "receipt_data": kwargs.get("receipt_data", {"total": 100.0}),
        "split_results": kwargs.get("split_results", {"Test": 100.0}),
        "currency": kwargs.get("currency", "USD"),
        "status": kwargs.get("status", "pending"),
    }
    split = Split(**data)
    db_session.add(split)
    return split
