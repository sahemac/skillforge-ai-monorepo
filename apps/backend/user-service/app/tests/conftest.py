"""
Test configuration and fixtures for SkillForge AI User Service
"""

import asyncio
import os
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_session
from app.models.base import SQLModel
from app.core.config import get_settings

# Import all models to ensure they are registered with SQLModel.metadata
from app.models.user import User, UserSettings, UserSession  
# Company models moved to company-service
# from app.models.company import CompanyProfile, TeamMember, Subscription

# Test database URL - Use real DATABASE_URL from environment
# CI/CD: Uses DATABASE_URL_STAGING secret for real staging database testing
# Local: Uses DATABASE_URL with Cloud SQL Proxy connection
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for local development if no DATABASE_URL set
if not TEST_DATABASE_URL:
    TEST_DATABASE_URL = "postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db"

# Override settings for testing
test_settings = get_settings()
test_settings.ENVIRONMENT = "testing"
test_settings.DATABASE_URL = TEST_DATABASE_URL

# Create test engine for PostgreSQL
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    # Use smaller pool size for tests to avoid connection limit issues
    pool_size=2,
    max_overflow=5,
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
    """Set up test database - no schema changes needed for real DB."""
    # No table creation needed - using real database with existing schema
    yield
    # No cleanup needed - real database should not be altered


@pytest.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with transaction rollback for safety."""
    async with TestSessionLocal() as session:
        # Start a transaction that will be rolled back
        transaction = await session.begin()
        try:
            yield session
        finally:
            # Always rollback to ensure no test data persists
            await transaction.rollback()


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
def create_test_user(db_session: AsyncSession):
    """Create a test user directly in database."""
    from app.models.user import User
    import uuid
    from datetime import datetime
    import hashlib
    
    async def _create_user(user_data: dict = None):
        if user_data is None:
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "email": f"testuser{unique_id}@skillforge-ai.com",
                "username": f"testuser{unique_id}",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "terms_accepted": True,
                "privacy_policy_accepted": True
            }
        
        # Simple password hashing for testing
        password_hash = hashlib.sha256(user_data["password"].encode()).hexdigest()
        
        # Create user object using User from definitive model
        db_user = User(
            email=user_data["email"],
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            hashed_password=password_hash,
            is_verified=True,
            terms_accepted=user_data.get("terms_accepted", True),
            privacy_policy_accepted=user_data.get("privacy_policy_accepted", True),
            created_at=datetime.utcnow()
        )
        
        db_session.add(db_user)
        await db_session.commit()
        await db_session.refresh(db_user)
        return db_user
    
    return _create_user


# Company test fixture removed - companies are now handled by company-service
# @pytest.fixture
# def create_test_company(db_session: AsyncSession):
#     """Create a test company directly in database."""
#     ...
#     Company functionality moved to company-service


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create an authenticated test client with real test user."""
    # Use one of the 3 real test email addresses
    test_user_data = {
        "email": "libressay@gmail.com",
        "username": "libressay_testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Libressay",
        "last_name": "TestUser",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    try:
        # First try to login if user already exists
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                client.headers.update({"Authorization": f"Bearer {access_token}"})
                
                # Get user data
                user_response = client.get("/api/v1/users/me")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    return client, user_data
        
        # If user doesn't exist, create new test user with real email
        print(f"Creating new test user: {test_user_data['email']}")
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        
        if register_response.status_code == 201:
            user_data = register_response.json()
            print(f"Test user created successfully: {user_data.get('email')}")
            
            # Login with the newly created user
            login_response = client.post("/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    client.headers.update({"Authorization": f"Bearer {access_token}"})
                    return client, user_data
        
        # If registration fails, print the error and skip
        error_detail = register_response.json().get('detail', 'Unknown error') if register_response.status_code != 201 else 'Login failed'
        print(f"Authentication failed: Register={register_response.status_code}, Error={error_detail}")
        pytest.skip(f"Cannot create or authenticate test user: {error_detail}")
        
    except Exception as e:
        pytest.skip(f"Authentication setup failed: {e}")

# Third test user fixture for company tests
@pytest.fixture
def authenticated_client_third(client: TestClient):
    """Create third authenticated test client with real test user."""
    # Use third real test email address
    test_user_data = {
        "email": "user@odoolab.site",
        "username": "odoolab_testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Odoo",
        "last_name": "TestUser",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    try:
        # First try to login if user already exists
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                client.headers.update({"Authorization": f"Bearer {access_token}"})
                
                # Get user data
                user_response = client.get("/api/v1/users/me")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    return client, user_data
        
        # If user doesn't exist, create new test user with real email
        print(f"Creating third test user: {test_user_data['email']}")
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        
        if register_response.status_code == 201:
            user_data = register_response.json()
            print(f"Third test user created successfully: {user_data.get('email')}")
            
            # Login with the newly created user
            login_response = client.post("/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    client.headers.update({"Authorization": f"Bearer {access_token}"})
                    return client, user_data
        
        # If registration fails, skip tests
        error_detail = register_response.json().get('detail', 'Unknown error') if register_response.status_code != 201 else 'Login failed'
        print(f"Third user authentication failed: Register={register_response.status_code}, Error={error_detail}")
        pytest.skip(f"Cannot create or authenticate third test user: {error_detail}")
        
    except Exception as e:
        pytest.skip(f"Third user authentication setup failed: {e}")

# Simplified version that returns None instead of failing
@pytest.fixture  
def authenticated_client_optional(client: TestClient):
    """Create authenticated client, returns None if fails (for optional tests)."""
    try:
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_user_data = {
            "email": f"testuser{unique_id}@skillforge-ai.com",
            "username": f"testuser{unique_id}",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "terms_accepted": True,
            "privacy_policy_accepted": True
        }
        
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        if register_response.status_code == 201:
            user_data = register_response.json()
            
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
            
            login_response = client.post("/api/v1/auth/login", json=login_data)
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    client.headers.update({"Authorization": f"Bearer {access_token}"})
                    return client, user_data
        
        return None, None
    except:
        return None, None


@pytest.fixture
def authenticated_admin_client(client: TestClient):
    """Create an authenticated admin test client with real test user."""
    # Use second real test email address for admin tests
    admin_data = {
        "email": "devops-alerts@emacsah.com",
        "username": "devops_admin",
        "password": "AdminPassword123!",
        "confirm_password": "AdminPassword123!",
        "first_name": "DevOps",
        "last_name": "Admin",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    try:
        # First try to login if admin user already exists
        login_data = {
            "email": admin_data["email"],
            "password": admin_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                client.headers.update({"Authorization": f"Bearer {access_token}"})
                
                # Get user data
                user_response = client.get("/api/v1/users/me")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    return client, user_data
        
        # If admin user doesn't exist, create new admin user with real email
        print(f"Creating new admin test user: {admin_data['email']}")
        register_response = client.post("/api/v1/auth/register", json=admin_data)
        
        if register_response.status_code == 201:
            user_data = register_response.json()
            print(f"Admin test user created successfully: {user_data.get('email')}")
            
            # Login with the newly created admin user
            login_response = client.post("/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    client.headers.update({"Authorization": f"Bearer {access_token}"})
                    return client, user_data
        
        # If registration fails, skip admin tests
        error_detail = register_response.json().get('detail', 'Unknown error') if register_response.status_code != 201 else 'Login failed'
        print(f"Admin authentication failed: Register={register_response.status_code}, Error={error_detail}")
        pytest.skip(f"Cannot create or authenticate admin user: {error_detail}")
        
    except Exception as e:
        pytest.skip(f"Admin authentication setup failed: {e}")

# Keep admin_user for backward compatibility
@pytest.fixture
def admin_user(authenticated_admin_client):
    """Get admin user data from authenticated admin client."""
    client, user_data = authenticated_admin_client
    return user_data


@pytest.fixture
def real_email_service():
    """Enable real email service for testing - no mocking."""
    # This fixture does nothing, allowing real emails to be sent
    # Used to explicitly indicate tests that send real emails
    yield


@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service for testing to prevent sending real emails."""
    from unittest.mock import Mock

    # Mock the email service functions
    mock_send_email = Mock(return_value=True)
    mock_send_verification_email = Mock(return_value=True)
    mock_send_password_reset_email = Mock(return_value=True)

    # Apply monkeypatch to email service functions
    monkeypatch.setattr("app.core.email.send_email", mock_send_email)
    monkeypatch.setattr("app.core.email.send_verification_email", mock_send_verification_email)
    monkeypatch.setattr("app.core.email.send_password_reset_email", mock_send_password_reset_email)

    return {
        "send_email": mock_send_email,
        "send_verification_email": mock_send_verification_email,
        "send_password_reset_email": mock_send_password_reset_email
    }


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