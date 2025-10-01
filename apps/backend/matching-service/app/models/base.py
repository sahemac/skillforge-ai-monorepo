"""
Base models and mixins for SkillForge AI Matching Service
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


def generate_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class UUIDMixin(SQLModel):
    """Mixin for UUID primary key."""

    id: str = Field(
        default_factory=generate_uuid,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=False), primary_key=True)
    )


class BaseModel(UUIDMixin, TimestampMixin, SQLModel):
    """Base model with UUID and timestamps."""

    class Config:
        """SQLModel configuration."""
        from_attributes = True
        str_strip_whitespace = True
        validate_assignment = True
        use_enum_values = True
        populate_by_name = True


class MatchingStatus:
    """Matching status constants."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MatchingType:
    """Matching type constants."""
    USER_TO_PROJECT = "user_to_project"
    PROJECT_TO_USER = "project_to_user"
    USER_TO_USER = "user_to_user"
    SKILL_BASED = "skill_based"
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"


class PreferenceType:
    """User preference types."""
    LOCATION = "location"
    SALARY = "salary"
    SKILLS = "skills"
    PROJECT_TYPE = "project_type"
    EXPERIENCE_LEVEL = "experience_level"
    WORK_MODE = "work_mode"