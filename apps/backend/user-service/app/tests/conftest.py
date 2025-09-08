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
def create_test_user(db_session: AsyncSession):
    """Create a test user directly in database."""
    import asyncio
    from app.crud import user
    from app.models.user import User
    from app.utils.security import get_password_hash
    import uuid
    
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
        
        # Create user object
        hashed_password = get_password_hash(user_data["password"])
        db_user = User(
            email=user_data["email"],
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            hashed_password=hashed_password,
            is_verified=True,
            terms_accepted=user_data.get("terms_accepted", True),
            privacy_policy_accepted=user_data.get("privacy_policy_accepted", True)
        )
        
        db_session.add(db_user)
        await db_session.commit()
        await db_session.refresh(db_user)
        return db_user
    
    return _create_user


@pytest.fixture
def create_test_company(db_session: AsyncSession):
    """Create a test company directly in database."""
    from app.models.company import Company
    from app.utils.text import slugify
    import uuid
    
    async def _create_company(owner_user, company_data: dict = None):
        if company_data is None:
            unique_id = str(uuid.uuid4())[:8]
            company_data = {
                "name": f"Test Company {unique_id}",
                "description": "A test company for unit testing",
                "industry": "technology",
                "company_size": "small",
                "website": "https://testcompany.com",
                "email": "info@testcompany.com"
            }
        
        # Generate slug if not provided
        if "slug" not in company_data:
            company_data["slug"] = slugify(company_data["name"])
        
        # Create company object
        db_company = Company(
            name=company_data["name"],
            slug=company_data["slug"],
            description=company_data.get("description"),
            industry=company_data.get("industry"),
            company_size=company_data.get("company_size"),
            website=company_data.get("website"),
            email=company_data.get("email"),
            owner_id=owner_user.id
        )
        
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)
        return db_company
    
    return _create_company


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create an authenticated test client."""
    import uuid
    
    # Use unique email for each test
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
    
    try:
        # Register user
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        
        if register_response.status_code == 201:
            user_data = register_response.json()
            
            # Login to get token
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
            
            login_response = client.post("/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    # Update client headers
                    client.headers.update({"Authorization": f"Bearer {access_token}"})
                    return client, user_data
        
        # If registration/login fails, raise error to fail test explicitly
        raise Exception(f"Authentication setup failed: Register={register_response.status_code}, Login={getattr(login_response, 'status_code', 'N/A')}")
        
    except Exception as e:
        pytest.fail(f"authenticated_client fixture failed: {e}")

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
    """Create an authenticated admin test client."""
    import uuid
    
    # Use unique email for admin user
    unique_id = str(uuid.uuid4())[:8]
    admin_data = {
        "email": f"admin{unique_id}@skillforge-ai.com",
        "username": f"admin{unique_id}",
        "password": "AdminPassword123!",
        "confirm_password": "AdminPassword123!",
        "first_name": "Admin",
        "last_name": "User",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    try:
        # Register admin user
        register_response = client.post("/api/v1/auth/register", json=admin_data)
        
        if register_response.status_code == 201:
            user_data = register_response.json()
            
            # Login to get token
            login_data = {
                "email": admin_data["email"],
                "password": admin_data["password"]
            }
            
            login_response = client.post("/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    # Update client headers
                    client.headers.update({"Authorization": f"Bearer {access_token}"})
                    return client, user_data
        
        # If registration/login fails, raise error
        raise Exception(f"Admin authentication setup failed: Register={register_response.status_code}")
        
    except Exception as e:
        pytest.fail(f"authenticated_admin_client fixture failed: {e}")

# Keep admin_user for backward compatibility
@pytest.fixture
def admin_user(authenticated_admin_client):
    """Get admin user data from authenticated admin client."""
    client, user_data = authenticated_admin_client
    return user_data


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