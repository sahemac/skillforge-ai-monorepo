#!/usr/bin/env python3
"""
Tests unitaires simples pour les modèles et CRUD
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.models.base import SQLModel
from app.models.user_simple import User, UserRole, UserStatus, UserSkillLevel
from app.models.company_simple import CompanyProfile, CompanySize, IndustryType
from app.core.security import get_password_hash, verify_password

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    """Create a test database session."""
    # Create test engine
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create test session factory
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await test_engine.dispose()

@pytest.mark.asyncio
async def test_user_model_creation(db_session):
    """Test creating a user model."""
    session = await db_session.__anext__()
    """Test creating a user model."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": get_password_hash("password123"),
        "first_name": "Test",
        "last_name": "User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE,
        "is_email_verified": True,
        "is_active": True,
        "experience_level": UserSkillLevel.BEGINNER,
        "language_preference": "fr",
        "newsletter_subscribed": True
    }
    
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.role == UserRole.USER
    assert user.status == UserStatus.ACTIVE
    assert user.experience_level == UserSkillLevel.BEGINNER
    assert verify_password("password123", user.hashed_password)

@pytest.mark.asyncio
async def test_company_model_creation(db_session):
    """Test creating a company model."""
    company_data = {
        "name": "Test Company",
        "slug": "test-company",
        "description": "A test company",
        "industry": IndustryType.TECHNOLOGY,
        "size": CompanySize.STARTUP,
        "is_active": True,
        "is_verified": False,
        "plan_type": "free"
    }
    
    company = CompanyProfile(**company_data)
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    
    assert company.id is not None
    assert company.name == "Test Company"
    assert company.slug == "test-company"
    assert company.industry == IndustryType.TECHNOLOGY
    assert company.size == CompanySize.STARTUP

def test_enums():
    """Test enum values."""
    assert UserRole.USER == "user"
    assert UserRole.ADMIN == "admin"
    assert UserRole.PREMIUM_USER == "premium_user"
    
    assert UserStatus.ACTIVE == "active"
    assert UserStatus.INACTIVE == "inactive"
    
    assert UserSkillLevel.BEGINNER == "beginner"
    assert UserSkillLevel.EXPERT == "expert"
    
    assert CompanySize.STARTUP == "startup"
    assert CompanySize.ENTERPRISE == "enterprise"
    
    assert IndustryType.TECHNOLOGY == "technology"
    assert IndustryType.HEALTHCARE == "healthcare"

def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

@pytest.mark.asyncio
async def test_user_relationships(db_session):
    """Test basic user and company relationships."""
    # Create user
    user = User(
        email="user@example.com",
        username="user1",
        hashed_password=get_password_hash("password"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
        is_active=True,
        language_preference="en",
        newsletter_subscribed=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create company
    company = CompanyProfile(
        name="User Company",
        slug="user-company",
        industry=IndustryType.FINANCE,
        size=CompanySize.SMALL,
        is_active=True,
        is_verified=True,
        plan_type="premium"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    
    assert user.id is not None
    assert company.id is not None
    assert user.email == "user@example.com"
    assert company.name == "User Company"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])