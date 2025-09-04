"""
User model simplifié pour SkillForge AI User Service
Version temporaire pour éviter les erreurs SQLModel
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from enum import Enum
import uuid


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    EXPERT = "expert"
    PREMIUM_USER = "premium_user"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserSkillLevel(str, Enum):
    """User skill level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class User(SQLModel, table=True):
    """User model simplifié pour éviter les erreurs SQLModel."""
    
    __tablename__ = "users"
    
    # Primary Key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
    
    # Basic Information
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False, min_length=3, max_length=50)
    hashed_password: str = Field(nullable=False)
    
    # Profile Information
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    
    # User Status and Role
    role: UserRole = Field(default=UserRole.USER, nullable=False)
    status: UserStatus = Field(default=UserStatus.ACTIVE, nullable=False)
    is_email_verified: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    experience_level: Optional[UserSkillLevel] = Field(default=UserSkillLevel.BEGINNER)
    
    # Location and Language
    country: Optional[str] = Field(default=None, max_length=100)
    timezone: Optional[str] = Field(default=None, max_length=50)
    language_preference: str = Field(default="fr", max_length=10, nullable=False)
    
    # Basic preferences (as simple strings for now)
    newsletter_subscribed: bool = Field(default=True, nullable=False)


# Modèles supplémentaires requis pour les tests et CRUD
class UserSession(SQLModel, table=True):
    """Session utilisateur pour tracking."""
    __tablename__ = "user_sessions"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    session_token: str = Field(nullable=False, index=True)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)


class UserSettings(SQLModel, table=True):
    """Paramètres utilisateur."""
    __tablename__ = "user_settings"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, unique=True)
    theme: str = Field(default="light", nullable=False)
    language: str = Field(default="fr", nullable=False)
    email_notifications: bool = Field(default=True, nullable=False)
    push_notifications: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)


# Schémas pour l'API
class UserCreate(SQLModel):
    """Schema for creating a user."""
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserRead(SQLModel):
    """Schema for reading user data."""
    id: uuid.UUID
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class UserUpdate(SQLModel):
    """Schema for updating user data."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    language_preference: Optional[str] = None
    newsletter_subscribed: Optional[bool] = None