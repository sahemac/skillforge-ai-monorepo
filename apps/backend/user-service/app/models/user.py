"""
User model for SkillForge AI User Service
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON
from enum import Enum
import uuid

from .base import TimestampMixin, UUIDMixin


class UserRole(str, Enum):
    """User role enumeration for SkillForge AI business model."""
    ADMIN = "admin"                    # Platform administrator
    USER = "user"                      # Standard learner
    MODERATOR = "moderator"            # Community moderator
    PREMIUM_USER = "premium_user"      # Premium learner
    COMPANY_CONTACT = "company_contact"  # Company representative - creates projects


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserSkillLevel(str, Enum):
    """User skill level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class User(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    # From UUIDMixin
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    # Timestamp fields inherited from TimestampMixin
    
    # Basic Information
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False, min_length=3, max_length=50)
    hashed_password: str = Field(nullable=False)
    
    # Profile Information
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=1000)
    
    # Account Management
    role: UserRole = Field(default=UserRole.USER, nullable=False)
    status: UserStatus = Field(default=UserStatus.ACTIVE, nullable=False)
    is_email_verified: bool = Field(default=False, nullable=False)  # Correspond à la colonne PostgreSQL
    is_active: bool = Field(default=True, nullable=False)
    experience_level: Optional[UserSkillLevel] = Field(default=UserSkillLevel.BEGINNER)
    
    # Contact Information (correspond aux colonnes PostgreSQL existantes)
    country: Optional[str] = Field(default=None, max_length=200)
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    language_preference: str = Field(default="en", nullable=False)
    newsletter_subscribed: bool = Field(default=True, nullable=False)
    
    # Relationships
    company_profiles: List["CompanyProfile"] = Relationship(back_populates="owner")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: str
        }


class UserSettings(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """User settings and preferences."""
    
    __tablename__ = "user_settings"
    
    # Primary key from UUIDMixin
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    
    # UI Preferences
    theme: str = Field(default="light", nullable=False)  # light, dark, auto
    language: str = Field(default="en", nullable=False)
    
    # Notification Settings
    email_notifications: bool = Field(default=True, nullable=False)
    push_notifications: bool = Field(default=True, nullable=False)
    sms_notifications: bool = Field(default=False, nullable=False)
    
    # Privacy Settings
    profile_visibility: str = Field(default="public", nullable=False)  # public, private, contacts_only
    show_email: bool = Field(default=False, nullable=False)
    show_phone: bool = Field(default=False, nullable=False)
    
    # Learning Preferences
    learning_reminders: bool = Field(default=True, nullable=False)
    weekly_digest: bool = Field(default=True, nullable=False)
    skill_recommendations: bool = Field(default=True, nullable=False)
    
    # Additional Settings
    custom_settings: Optional[dict] = Field(default={}, sa_column=Column(JSON))


class UserSession(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """User session tracking."""
    
    __tablename__ = "user_sessions"
    
    # Primary key from UUIDMixin
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    session_token: str = Field(unique=True, index=True, nullable=False)
    refresh_token: Optional[str] = Field(unique=True, index=True, default=None)
    
    # Session Information
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    device_info: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    
    # Session Management
    expires_at: datetime = Field(nullable=False)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    logout_at: Optional[datetime] = Field(default=None)