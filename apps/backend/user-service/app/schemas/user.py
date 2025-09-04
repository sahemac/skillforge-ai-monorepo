"""
User schemas for SkillForge AI User Service
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

from app.models.user_simple import UserRole, UserStatus, UserSkillLevel


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    timezone: Optional[str] = Field("UTC", max_length=50)
    job_title: Optional[str] = Field(None, max_length=200)
    experience_level: Optional[UserSkillLevel] = UserSkillLevel.BEGINNER
    skills: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    newsletter_subscribed: bool = True


# Request schemas
class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    terms_accepted: bool = Field(..., description="User must accept terms and conditions")
    privacy_policy_accepted: bool = Field(..., description="User must accept privacy policy")
    
    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @field_validator("terms_accepted")
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError("Terms and conditions must be accepted")
        return v
    
    @field_validator("privacy_policy_accepted")  
    def privacy_policy_must_be_accepted(cls, v):
        if not v:
            raise ValueError("Privacy policy must be accepted")
        return v
    
    @field_validator("username")
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").replace(".", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, underscores, hyphens, and periods")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    timezone: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=200)
    experience_level: Optional[UserSkillLevel] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    newsletter_subscribed: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """Schema for password updates."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("confirm_new_password")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("New passwords do not match")
        return v


class UserRoleUpdate(BaseModel):
    """Schema for user role updates (admin only)."""
    role: UserRole
    is_superuser: Optional[bool] = None


class UserStatusUpdate(BaseModel):
    """Schema for user status updates (admin only)."""
    status: UserStatus
    is_active: Optional[bool] = None


# Response schemas
class UserResponse(BaseModel):
    """Schema for user response data."""
    id: UUID
    email: EmailStr
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    phone_number: Optional[str]
    location: Optional[str]
    timezone: str
    job_title: Optional[str]
    experience_level: UserSkillLevel
    skills: List[str]
    interests: List[str]
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    is_premium: bool
    premium_expires_at: Optional[datetime]
    newsletter_subscribed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    """Schema for public user profile data."""
    id: UUID
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]
    job_title: Optional[str]
    experience_level: UserSkillLevel
    skills: List[str]
    interests: List[str]
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserAdminResponse(UserResponse):
    """Schema for admin user response with additional fields."""
    is_superuser: bool
    email_verified_at: Optional[datetime]
    failed_login_attempts: int
    account_locked_until: Optional[datetime]
    terms_accepted_at: Optional[datetime]
    privacy_policy_accepted_at: Optional[datetime]
    metadata: Dict[str, Any]


# Authentication schemas
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class UserRegister(UserCreate):
    """Schema for user registration (alias for UserCreate)."""
    pass


# Token schemas
class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data schema."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class RefreshToken(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


# Email verification schemas
class EmailVerificationRequest(BaseModel):
    """Schema for requesting email verification."""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Schema for confirming email verification."""
    token: str


# Password reset schemas
class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("confirm_new_password")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


# User settings schemas
class UserSettingsResponse(BaseModel):
    """Schema for user settings response."""
    id: UUID
    user_id: UUID
    theme: str
    language: str
    email_notifications: bool
    push_notifications: bool
    sms_notifications: bool
    profile_visibility: str
    show_email: bool
    show_phone: bool
    learning_reminders: bool
    weekly_digest: bool
    skill_recommendations: bool
    custom_settings: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""
    theme: Optional[str] = Field(None, pattern=r"^(light|dark|auto)$")
    language: Optional[str] = Field(None, max_length=5)
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    profile_visibility: Optional[str] = Field(None, pattern=r"^(public|private|contacts_only)$")
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    learning_reminders: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    skill_recommendations: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None


# List responses
class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class UserPublicListResponse(BaseModel):
    """Schema for paginated public user list response."""
    users: List[UserPublicResponse]
    total: int
    page: int
    size: int
    pages: int