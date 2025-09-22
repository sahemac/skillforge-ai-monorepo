"""
Company schemas for SkillForge AI Company Service
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from uuid import UUID

from app.models.company import CompanySize, IndustryType


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    industry: Optional[IndustryType] = None
    company_size: Optional[CompanySize] = None
    founded_year: Optional[int] = Field(None, ge=1800, le=2024)
    employee_count: Optional[int] = Field(None, ge=0)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    twitter_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)
    skills_focus: Optional[List[str]] = Field(default_factory=list)
    learning_goals: Optional[List[str]] = Field(default_factory=list)
    billing_email: Optional[EmailStr] = None


class CompanyCreate(CompanyBase):
    """Company creation schema."""
    pass


class CompanyUpdate(BaseModel):
    """Company update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    industry: Optional[IndustryType] = None
    company_size: Optional[CompanySize] = None
    founded_year: Optional[int] = Field(None, ge=1800, le=2024)
    employee_count: Optional[int] = Field(None, ge=0)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    twitter_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)
    skills_focus: Optional[List[str]] = None
    learning_goals: Optional[List[str]] = None
    billing_email: Optional[EmailStr] = None


class CompanyResponse(CompanyBase):
    """Company response schema."""
    id: UUID
    owner_id: UUID
    subscription_plan: str
    subscription_status: str
    is_active: bool
    is_verified: bool
    verified_at: Optional[datetime] = None
    settings: Optional[dict] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompanyPublicResponse(BaseModel):
    """Public company response schema (limited fields)."""
    id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[IndustryType] = None
    company_size: Optional[CompanySize] = None
    founded_year: Optional[int] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    github_url: Optional[str] = None
    skills_focus: Optional[List[str]] = Field(default_factory=list)
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Company list response schema."""
    companies: List[CompanyResponse]
    total: int
    page: int
    size: int
    pages: int


class CompanyPublicListResponse(BaseModel):
    """Public company list response schema."""
    companies: List[CompanyPublicResponse]
    total: int
    page: int
    size: int
    pages: int


# Team member schemas
class TeamMemberBase(BaseModel):
    """Base team member schema."""
    role: str = Field(..., max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    permissions: Optional[List[str]] = Field(default_factory=list)


class TeamMemberCreate(TeamMemberBase):
    """Team member creation schema."""
    user_id: UUID


class TeamMemberUpdate(BaseModel):
    """Team member update schema."""
    role: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(TeamMemberBase):
    """Team member response schema."""
    id: UUID
    company_id: UUID
    user_id: UUID
    is_active: bool
    joined_at: datetime
    left_at: Optional[datetime] = None
    invited_by: Optional[UUID] = None
    invited_at: Optional[datetime] = None
    invitation_accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeamMemberListResponse(BaseModel):
    """Team member list response schema."""
    members: List[TeamMemberResponse]
    total: int
    page: int
    size: int
    pages: int


# Subscription schemas
class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    plan_name: str = Field(..., max_length=100)
    plan_price: float = Field(..., ge=0)
    billing_cycle: str = Field(..., max_length=20)
    currency: str = Field(default="USD", max_length=3)
    seats_included: int = Field(default=1, ge=1)


class SubscriptionCreate(SubscriptionBase):
    """Subscription creation schema."""
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None


class SubscriptionUpdate(BaseModel):
    """Subscription update schema."""
    plan_name: Optional[str] = Field(None, max_length=100)
    plan_price: Optional[float] = Field(None, ge=0)
    billing_cycle: Optional[str] = Field(None, max_length=20)
    currency: Optional[str] = Field(None, max_length=3)
    status: Optional[str] = Field(None, max_length=20)
    seats_included: Optional[int] = Field(None, ge=1)
    seats_used: Optional[int] = Field(None, ge=0)


class SubscriptionResponse(SubscriptionBase):
    """Subscription response schema."""
    id: UUID
    company_id: UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    seats_used: int
    subscription_metadata: Optional[dict] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True