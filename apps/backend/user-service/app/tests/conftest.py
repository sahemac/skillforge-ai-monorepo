"""
Test configuration and fixtures for SkillForge AI User Service
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_session
from app.models.base import SQLModel
from app.core.config import get_settings

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override settings for testing
test_settings = get_settings()
test_settings.ENVIRONMENT = "testing"
test_settings.DATABASE_URL = TEST_DATABASE_URL

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


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency."""
    async def _override_get_db():
        yield db_session
    
    # We'll handle dependency override in individual test app instances
    yield _override_get_db


@pytest.fixture
def client(override_get_db) -> Generator[TestClient, None, None]:
    """Create a test client."""
    from fastapi import FastAPI
    
    # Create a minimal test app instead of importing main.py
    test_app = FastAPI(
        title="SkillForge AI User Service - Tests",
        description="Test version of the API",
        version="1.0.0",
    )
    
    # Override the database dependency
    test_app.dependency_overrides[get_session] = override_get_db
    
    # Import and include only necessary routers for testing
    try:
        from app.api.v1 import api_router
        test_app.include_router(api_router, prefix="/api/v1")
    except ImportError:
        # If routers can't be imported, create minimal test routes
        @test_app.get("/")
        def read_root():
            return {"message": "Test API"}
    
    with TestClient(test_app) as test_client:
        yield test_client
    
    # Clear overrides after test
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@skillforge-ai.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }


@pytest.fixture
def sample_company_data():
    """Sample company data for testing."""
    return {
        "name": "Test Company Inc.",
        "description": "A test company for unit testing",
        "industry": "technology",
        "company_size": "small",
        "website": "https://testcompany.com",
        "email": "info@testcompany.com"
    }


@pytest.fixture
def create_test_user(client: TestClient):
    """Create a test user."""
    def _create_user(user_data: dict = None):
        if user_data is None:
            user_data = {
                "email": "test@skillforge-ai.com",
                "username": "testuser",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "terms_accepted": True,
                "privacy_policy_accepted": True
            }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            return response.json()
        
        return None
    
    return _create_user


@pytest.fixture
def create_test_company(client: TestClient):
    """Create a test company."""
    def _create_company(auth_client, company_data: dict = None):
        if company_data is None:
            company_data = {
                "name": "Test Company Inc.",
                "description": "A test company for unit testing",
                "industry": "technology",
                "company_size": "small",
                "website": "https://testcompany.com",
                "email": "info@testcompany.com"
            }
        
        response = auth_client.post("/api/v1/companies/", json=company_data)
        if response.status_code == 201:
            return response.json()
        
        return None
    
    return _create_company


@pytest.fixture
def authenticated_client(client: TestClient, create_test_user):
    """Create an authenticated test client."""
    # Create a simple authenticated client for synchronous tests
    # We'll create a test token directly
    test_user_data = {
        "email": "test@skillforge-ai.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    # Register user first
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    if register_response.status_code == 201:
        # Login to get token
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # Add authorization header to client
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            
            return client, test_user_data
    
    # Return client without auth if registration/login failed
    return client, None


@pytest.fixture
def admin_user(client: TestClient):
    """Create an admin user."""
    admin_data = {
        "email": "admin@skillforge-ai.com",
        "username": "admin",
        "password": "AdminPassword123!",
        "confirm_password": "AdminPassword123!",
        "first_name": "Admin",
        "last_name": "User",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    # Register admin user
    response = client.post("/api/v1/auth/register", json=admin_data)
    if response.status_code == 201:
        return admin_data
    
    return None


@pytest.fixture
def authenticated_admin_client(client: TestClient, admin_user):
    """Create an authenticated admin test client."""
    if admin_user:
        # Login to get token
        login_data = {
            "email": admin_user["email"],
            "password": admin_user["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # Add authorization header to client
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            
            return client, admin_user
    
    return client, None


@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service for testing."""
    def mock_send_email(*args, **kwargs):
        return True
    
    def mock_send_verification_email(*args, **kwargs):
        return True
    
    def mock_send_password_reset_email(*args, **kwargs):
        return True
    
    # Mock at module level to avoid import issues
    try:
        import app.utils.email
        monkeypatch.setattr(app.utils.email, "send_email", mock_send_email)
        monkeypatch.setattr(app.utils.email, "send_verification_email", mock_send_verification_email)
        monkeypatch.setattr(app.utils.email, "send_password_reset_email", mock_send_password_reset_email)
    except ImportError:
        # If email module can't be imported, create mock module
        class MockEmailModule:
            send_email = staticmethod(mock_send_email)
            send_verification_email = staticmethod(mock_send_verification_email)
            send_password_reset_email = staticmethod(mock_send_password_reset_email)
        
        import sys
        sys.modules['app.utils.email'] = MockEmailModule()


# Test data factories
class UserFactory:
    """Factory for creating test users."""
    
    @staticmethod
    def build(email: str = None, username: str = None, **kwargs):
        """Build user data."""
        base_data = {
            "email": email or "user@example.com",
            "username": username or "testuser",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "terms_accepted": True,
            "privacy_policy_accepted": True
        }
        base_data.update(kwargs)
        return base_data


class CompanyFactory:
    """Factory for creating test companies."""
    
    @staticmethod
    def build(name: str = None, **kwargs):
        """Build company data."""
        base_data = {
            "name": name or "Test Company",
            "description": "A test company",
            "industry": "technology",
            "company_size": "small",
            "website": "https://example.com",
            "email": "info@example.com"
        }
        base_data.update(kwargs)
        return base_data


# Test utilities
def assert_response_error(response, status_code: int, detail: str = None):
    """Assert response has expected error."""
    assert response.status_code == status_code
    if detail:
        assert detail in response.json()["detail"]


def assert_user_response(response_data: dict, expected_email: str = None):
    """Assert user response has expected fields."""
    required_fields = ["id", "email", "username", "first_name", "last_name", "created_at"]
    for field in required_fields:
        assert field in response_data
    
    if expected_email:
        assert response_data["email"] == expected_email
    
    # Sensitive fields should not be present
    sensitive_fields = ["hashed_password", "failed_login_attempts"]
    for field in sensitive_fields:
        assert field not in response_data


def assert_company_response(response_data: dict, expected_name: str = None):
    """Assert company response has expected fields."""
    required_fields = ["id", "name", "slug", "owner_id", "created_at"]
    for field in required_fields:
        assert field in response_data
    
    if expected_name:
        assert response_data["name"] == expected_name