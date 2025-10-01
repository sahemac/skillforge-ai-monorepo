"""
Test configuration and fixtures for SkillForge AI Matching Service
"""

import asyncio
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.models import *


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_session: Session) -> Generator[TestClient, None, None]:
    """Create test client with test database session."""

    def get_test_session():
        return test_session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_profile(test_session: Session) -> MatchingProfile:
    """Create a sample user profile for testing."""
    profile = MatchingProfile(
        user_id="test-user-123",
        user_type="learner",
        profile_data={
            "name": "John Doe",
            "bio": "Software developer with 3 years experience"
        },
        skills=["python", "javascript", "react", "fastapi"],
        interests=["web development", "machine learning", "startup"],
        experience_level="intermediate",
        preferred_location="San Francisco",
        preferred_work_mode="hybrid",
        salary_expectations={
            "min_salary": 80000,
            "max_salary": 120000,
            "currency": "USD"
        },
        matching_radius_km=25.0,
        is_active=True,
        profile_completeness_score=0.8
    )

    test_session.add(profile)
    test_session.commit()
    test_session.refresh(profile)
    return profile


@pytest.fixture
def sample_company_profile(test_session: Session) -> MatchingProfile:
    """Create a sample company profile for testing."""
    profile = MatchingProfile(
        user_id="test-company-456",
        user_type="company",
        profile_data={
            "name": "TechCorp Inc",
            "description": "Leading technology company focused on innovation"
        },
        skills=["python", "react", "aws", "docker", "kubernetes"],
        interests=["scalable systems", "microservices", "cloud native"],
        experience_level="intermediate",
        preferred_location="San Francisco",
        preferred_work_mode="hybrid",
        salary_expectations={
            "min_salary": 90000,
            "max_salary": 140000,
            "currency": "USD"
        },
        matching_radius_km=50.0,
        is_active=True,
        profile_completeness_score=0.9
    )

    test_session.add(profile)
    test_session.commit()
    test_session.refresh(profile)
    return profile


@pytest.fixture
def sample_match_result(
    test_session: Session,
    sample_user_profile: MatchingProfile,
    sample_company_profile: MatchingProfile
) -> MatchResult:
    """Create a sample match result for testing."""
    match = MatchResult(
        user_id=sample_user_profile.user_id,
        target_id=sample_company_profile.user_id,
        target_type=sample_company_profile.user_type,
        matching_type="user_to_project",
        algorithm_version="1.0.0",
        overall_score=0.75,
        skill_score=0.8,
        experience_score=0.7,
        location_score=1.0,
        preference_score=0.6,
        semantic_score=0.7,
        rank_position=1,
        confidence_level=0.8,
        match_reasons=["Strong skill overlap", "Location match", "Experience compatibility"],
        skill_overlaps=["python", "react"],
        missing_skills=["aws", "docker", "kubernetes"],
        match_metadata={"algorithm_version": "1.0.0"},
        computation_time_ms=125.5,
        status="completed",
        is_mutual=False,
        is_active=True
    )

    test_session.add(match)
    test_session.commit()
    test_session.refresh(match)
    return match


@pytest.fixture
def sample_preference(
    test_session: Session,
    sample_user_profile: MatchingProfile
) -> UserPreference:
    """Create a sample user preference for testing."""
    preference = UserPreference(
        user_id=sample_user_profile.user_id,
        profile_id=sample_user_profile.id,
        preference_type="work_mode",
        preference_name="Remote Work Preference",
        preference_value={
            "work_mode": "hybrid",
            "flexibility": "required"
        },
        priority=1,
        weight=2.0,
        is_mandatory=True,
        is_flexible=False,
        is_active=True,
        preference_metadata={
            "created_from_template": "Remote Work Preference"
        }
    )

    test_session.add(preference)
    test_session.commit()
    test_session.refresh(preference)
    return preference


@pytest.fixture
def multiple_profiles(test_session: Session) -> list[MatchingProfile]:
    """Create multiple profiles for testing batch operations."""
    profiles = []

    for i in range(5):
        profile = MatchingProfile(
            user_id=f"test-user-{i}",
            user_type="learner" if i % 2 == 0 else "company",
            profile_data={"name": f"Test User {i}"},
            skills=[f"skill-{j}" for j in range(i+1, i+4)],
            interests=[f"interest-{j}" for j in range(i+1, i+3)],
            experience_level=["beginner", "intermediate", "advanced"][i % 3],
            preferred_location=["New York", "San Francisco", "Austin"][i % 3],
            preferred_work_mode=["remote", "hybrid", "onsite"][i % 3],
            is_active=True,
            profile_completeness_score=0.5 + (i * 0.1)
        )
        profiles.append(profile)

    test_session.add_all(profiles)
    test_session.commit()

    for profile in profiles:
        test_session.refresh(profile)

    return profiles


# Async fixtures for async testing
@pytest_asyncio.fixture
async def async_test_session(test_engine):
    """Create async test database session."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlmodel import SQLModel

    # Create async engine
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session
    async with AsyncSession(async_engine) as session:
        yield session


# Test data factories
class ProfileFactory:
    """Factory for creating test profiles."""

    @staticmethod
    def create_learner_profile(
        user_id: str = "test-learner",
        skills: list = None,
        experience_level: str = "intermediate"
    ) -> MatchingProfile:
        return MatchingProfile(
            user_id=user_id,
            user_type="learner",
            profile_data={"name": f"Learner {user_id}"},
            skills=skills or ["python", "javascript", "react"],
            interests=["web development", "backend"],
            experience_level=experience_level,
            preferred_location="Remote",
            preferred_work_mode="remote",
            is_active=True,
            profile_completeness_score=0.8
        )

    @staticmethod
    def create_company_profile(
        user_id: str = "test-company",
        skills: list = None,
        experience_level: str = "intermediate"
    ) -> MatchingProfile:
        return MatchingProfile(
            user_id=user_id,
            user_type="company",
            profile_data={"name": f"Company {user_id}"},
            skills=skills or ["python", "react", "aws", "docker"],
            interests=["scalable systems", "cloud"],
            experience_level=experience_level,
            preferred_location="San Francisco",
            preferred_work_mode="hybrid",
            is_active=True,
            profile_completeness_score=0.9
        )


# Test utilities
class TestUtils:
    """Utility functions for tests."""

    @staticmethod
    def assert_valid_uuid(uuid_string: str):
        """Assert that a string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(uuid_string)
        except ValueError:
            pytest.fail(f"'{uuid_string}' is not a valid UUID")

    @staticmethod
    def assert_score_in_range(score: float, min_val: float = 0.0, max_val: float = 1.0):
        """Assert that a score is within valid range."""
        assert min_val <= score <= max_val, f"Score {score} not in range [{min_val}, {max_val}]"

    @staticmethod
    def assert_timestamp_format(timestamp: str):
        """Assert that a timestamp string is in ISO format."""
        from datetime import datetime
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"'{timestamp}' is not a valid ISO timestamp")


# Performance testing fixtures
@pytest.fixture
def performance_profiles(test_session: Session) -> list[MatchingProfile]:
    """Create a large number of profiles for performance testing."""
    profiles = []

    for i in range(100):
        profile = MatchingProfile(
            user_id=f"perf-user-{i}",
            user_type="learner" if i % 2 == 0 else "company",
            profile_data={"name": f"Performance User {i}"},
            skills=[f"skill-{j}" for j in range(i % 10, (i % 10) + 5)],
            interests=[f"interest-{j}" for j in range(i % 5, (i % 5) + 3)],
            experience_level=["beginner", "intermediate", "advanced", "expert"][i % 4],
            preferred_location=f"City-{i % 10}",
            is_active=True,
            profile_completeness_score=0.1 + (i % 10) * 0.1
        )
        profiles.append(profile)

    test_session.add_all(profiles)
    test_session.commit()

    return profiles