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
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    PREMIUM_USER = "premium_user"


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
    
    # From TimestampMixin
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
    
    # Basic Information
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False, min_length=3, max_length=50)
    hashed_password: str = Field(nullable=False)
    
    # Profile Information
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=200)
    bio: Optional[str] = Field(default=None, max_length=1000)
    avatar_url: Optional[str] = Field(default=None)
    
    # Contact Information
    phone_number: Optional[str] = Field(default=None, max_length=20)
    location: Optional[str] = Field(default=None, max_length=200)
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    
    # Professional Information
    job_title: Optional[str] = Field(default=None, max_length=200)
    experience_level: Optional[UserSkillLevel] = Field(default=UserSkillLevel.BEGINNER)
    skills: Optional[List[str]] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    interests: Optional[List[str]] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    
    # Account Management
    role: UserRole = Field(default=UserRole.USER, nullable=False)
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    
    # Verification and Security
    email_verified_at: Optional[datetime] = Field(default=None)
    last_login_at: Optional[datetime] = Field(default=None)
    failed_login_attempts: int = Field(default=0, nullable=False)
    account_locked_until: Optional[datetime] = Field(default=None)
    
    # Subscription and Preferences
    is_premium: bool = Field(default=False, nullable=False)
    premium_expires_at: Optional[datetime] = Field(default=None)
    newsletter_subscribed: bool = Field(default=True, nullable=False)
    notification_preferences: str = Field(default="{}", sa_column=Column(JSON))
    
    # User Metadata (renamed to avoid conflict with SQLModel's metadata) 
    user_metadata: str = Field(default="{}", sa_column=Column(JSON))
    terms_accepted_at: Optional[datetime] = Field(default=None)
    privacy_policy_accepted_at: Optional[datetime] = Field(default=None)
    
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
    custom_settings: Optional[dict] = Field(default={}, sa_column_kwargs={"type_": "JSON"})


class UserSession(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """User session tracking."""
    
    __tablename__ = "user_sessions"
    
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    session_token: str = Field(unique=True, index=True, nullable=False)
    refresh_token: Optional[str] = Field(unique=True, index=True, default=None)
    
    # Session Information
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    device_info: Optional[dict] = Field(default={}, sa_column_kwargs={"type_": "JSON"})
    
    # Session Management
    expires_at: datetime = Field(nullable=False)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    logout_at: Optional[datetime] = Field(default=None)