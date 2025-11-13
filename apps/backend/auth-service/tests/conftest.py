"""
Pytest configuration and fixtures for auth-service tests
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.models import UserTwoFactor


# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/auth_service_test"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    database_url = os.getenv("DATABASE_URL")

    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for each test."""
    # Create a session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Rollback after each test to keep tests isolated
            await session.rollback()

        # Clean up all tables after each test
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE user_two_factor CASCADE"))
            await session.commit()


@pytest.fixture
def sample_user_id() -> str:
    """Generate a sample user UUID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_two_factor_secret() -> str:
    """Generate a sample 2FA secret."""
    return "JBSWY3DPEHPK3PXP"  # Standard TOTP secret


@pytest.fixture
def sample_backup_codes() -> list[str]:
    """Generate sample backup codes."""
    return [
        "ABC123-DEF456",
        "GHI789-JKL012",
        "MNO345-PQR678",
        "STU901-VWX234",
        "YZA567-BCD890",
    ]


@pytest_asyncio.fixture
async def sample_two_factor(
    db_session: AsyncSession,
    sample_user_id: str,
    sample_two_factor_secret: str,
    sample_backup_codes: list[str],
) -> UserTwoFactor:
    """Create a sample UserTwoFactor record in the database."""
    two_factor = UserTwoFactor(
        user_id=sample_user_id,
        secret=sample_two_factor_secret,
        backup_codes=sample_backup_codes,
        is_enabled=True,
    )

    db_session.add(two_factor)
    await db_session.commit()
    await db_session.refresh(two_factor)

    return two_factor


@pytest.fixture
def mock_user_data() -> dict:
    """Generate mock user data for testing."""
    user_id = str(uuid4())
    return {
        "id": user_id,
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True,
        "is_verified": True,
        "role": "LEARNER",
    }


@pytest.fixture
def multiple_mock_users() -> list[dict]:
    """Generate multiple mock users for testing."""
    return [
        {
            "id": str(uuid4()),
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "full_name": f"User {i}",
            "is_active": True,
            "is_verified": True,
            "role": "LEARNER",
        }
        for i in range(5)
    ]
