"""
Company Profile model for SkillForge AI User Service
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
import uuid

from .base import TimestampMixin, UUIDMixin


class CompanySize(str, Enum):
    """Company size enumeration."""
    STARTUP = "startup"  # 1-10 employees
    SMALL = "small"  # 11-50 employees
    MEDIUM = "medium"  # 51-200 employees
    LARGE = "large"  # 201-1000 employees
    ENTERPRISE = "enterprise"  # 1000+ employees


class IndustryType(str, Enum):
    """Industry type enumeration."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    MEDIA = "media"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    OTHER = "other"


class CompanyProfile(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """Company profile for organizations using SkillForge AI."""
    
    __tablename__ = "company_profiles"
    
    # Basic Information
    name: str = Field(nullable=False, max_length=200, index=True)
    slug: str = Field(unique=True, index=True, nullable=False, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)
    logo_url: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None, max_length=500)
    
    # Contact Information
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    
    # Address Information
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    
    # Company Details
    industry: Optional[IndustryType] = Field(default=None)
    company_size: Optional[CompanySize] = Field(default=None)
    founded_year: Optional[int] = Field(default=None, ge=1800, le=2024)
    employee_count: Optional[int] = Field(default=None, ge=0)
    
    # Social Media Links
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    twitter_url: Optional[str] = Field(default=None, max_length=500)
    facebook_url: Optional[str] = Field(default=None, max_length=500)
    github_url: Optional[str] = Field(default=None, max_length=500)
    
    # Business Information
    tax_id: Optional[str] = Field(default=None, max_length=50)
    registration_number: Optional[str] = Field(default=None, max_length=50)
    
    # SkillForge AI Specific
    skills_focus: Optional[List[str]] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    learning_goals: Optional[List[str]] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    
    # Subscription and Billing
    subscription_plan: str = Field(default="free", nullable=False)  # free, basic, premium, enterprise
    subscription_status: str = Field(default="active", nullable=False)  # active, suspended, cancelled
    billing_email: Optional[str] = Field(default=None, max_length=255)
    
    # Account Management
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    verification_token: Optional[str] = Field(default=None)
    verified_at: Optional[datetime] = Field(default=None)
    
    # Owner Information
    owner_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    owner: "User" = Relationship(back_populates="company_profiles")
    
    # Settings and Preferences
    settings: Optional[dict] = Field(default={}, sa_column_kwargs={"type_": "JSON"})
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: str
        }


class CompanyTeamMember(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """Team members associated with company profiles."""
    
    __tablename__ = "company_team_members"
    
    company_id: uuid.UUID = Field(foreign_key="company_profiles.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    
    # Role Information
    role: str = Field(nullable=False, max_length=100)  # admin, member, manager, etc.
    title: Optional[str] = Field(default=None, max_length=200)
    department: Optional[str] = Field(default=None, max_length=100)
    
    # Permissions
    permissions: Optional[List[str]] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    
    # Status
    is_active: bool = Field(default=True, nullable=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    left_at: Optional[datetime] = Field(default=None)
    
    # Invitation Information
    invited_by: Optional[uuid.UUID] = Field(foreign_key="users.id", default=None)
    invited_at: Optional[datetime] = Field(default=None)
    invitation_accepted_at: Optional[datetime] = Field(default=None)


class CompanySubscription(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """Company subscription and billing information."""
    
    __tablename__ = "company_subscriptions"
    
    company_id: uuid.UUID = Field(foreign_key="company_profiles.id", nullable=False, index=True)
    
    # Subscription Details
    plan_name: str = Field(nullable=False, max_length=100)
    plan_price: float = Field(nullable=False, ge=0)
    billing_cycle: str = Field(nullable=False, max_length=20)  # monthly, yearly
    currency: str = Field(default="USD", nullable=False, max_length=3)
    
    # Status and Dates
    status: str = Field(nullable=False, max_length=20)  # active, cancelled, past_due, etc.
    current_period_start: datetime = Field(nullable=False)
    current_period_end: datetime = Field(nullable=False)
    trial_start: Optional[datetime] = Field(default=None)
    trial_end: Optional[datetime] = Field(default=None)
    
    # Billing Information
    stripe_subscription_id: Optional[str] = Field(default=None, unique=True)
    stripe_customer_id: Optional[str] = Field(default=None)
    
    # Usage Tracking
    seats_included: int = Field(default=1, nullable=False, ge=1)
    seats_used: int = Field(default=0, nullable=False, ge=0)
    
    # Metadata
    metadata: Optional[dict] = Field(default={}, sa_column_kwargs={"type_": "JSON"})