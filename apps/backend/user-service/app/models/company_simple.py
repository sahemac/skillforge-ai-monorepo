"""
Company model simplifié pour SkillForge AI User Service
Version temporaire pour éviter les erreurs SQLModel
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from enum import Enum
import uuid


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


class CompanyProfile(SQLModel, table=True):
    """Company profile simplifié pour éviter les erreurs SQLModel."""
    
    __tablename__ = "company_profiles"
    
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
    
    # Basic Company Information
    name: str = Field(nullable=False, max_length=200)
    slug: str = Field(unique=True, index=True, nullable=False, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)
    website: Optional[str] = Field(default=None, max_length=500)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    
    # Company Details
    industry: IndustryType = Field(default=IndustryType.OTHER, nullable=False)
    size: CompanySize = Field(default=CompanySize.STARTUP, nullable=False)
    founded_year: Optional[int] = Field(default=None, ge=1800, le=2030)
    headquarters: Optional[str] = Field(default=None, max_length=200)
    
    # Contact Information
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    
    # Status and Settings
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    plan_type: str = Field(default="free", nullable=False, max_length=50)
    
    # Social Links (as simple strings for now)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    twitter_url: Optional[str] = Field(default=None, max_length=500)


class TeamMember(SQLModel, table=True):
    """Team member association table."""
    __tablename__ = "team_members"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    company_id: uuid.UUID = Field(foreign_key="company_profiles.id", nullable=False)
    
    # Member Details
    role: str = Field(default="member", nullable=False, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=200)
    
    # Status and Permissions
    is_admin: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    
    # Timestamps
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Subscription(SQLModel, table=True):
    """Subscription model for company plans."""
    __tablename__ = "subscriptions"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    # Foreign Keys
    company_id: uuid.UUID = Field(foreign_key="company_profiles.id", nullable=False)
    
    # Plan Details
    plan_name: str = Field(nullable=False, max_length=100)
    billing_cycle: str = Field(default="monthly", nullable=False)  # monthly, yearly
    seats_included: int = Field(default=5, nullable=False, ge=1)
    seats_used: int = Field(default=0, nullable=False, ge=0)
    
    # Pricing
    price_per_seat: float = Field(default=0.0, nullable=False, ge=0)
    total_amount: float = Field(default=0.0, nullable=False, ge=0)
    
    # Status and Dates
    is_active: bool = Field(default=True, nullable=False)
    trial_ends_at: Optional[datetime] = Field(default=None)
    current_period_start: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    current_period_end: datetime = Field(nullable=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)