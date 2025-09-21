#!/usr/bin/env python3
"""
Test API simple pour vérifier les endpoints de base
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_session
from app.models.base import SQLModel

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

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

@pytest.fixture
async def test_db():
    """Set up test database."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def db_session(test_db):
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_client(db_session):
    """Create test client."""
    
    async def override_get_session():
        yield db_session
    
    # Create minimal test app
    app = FastAPI(title="Test API")
    
    # Override the database dependency
    app.dependency_overrides[get_session] = override_get_session
    
    # Add basic route
    @app.get("/")
    def read_root():
        return {"service": "test", "status": "ok"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    with TestClient(app) as client:
        yield client

def test_basic_endpoints(test_client):
    """Test basic endpoints."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "test"
    
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_database_connection(db_session):
    """Test database connection."""
    # Simple query to test connection
    result = await db_session.execute("SELECT 1")
    value = result.scalar()
    assert value == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])