"""
Company schemas for SkillForge AI User Service
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl
from uuid import UUID

from app.models.company_simple import CompanySize, IndustryType


# Base schemas
class CompanyBase(BaseModel):
    """Base company schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
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
    skills_focus: Optional[List[str]] = []
    learning_goals: Optional[List[str]] = []


# Request schemas
class CompanyCreate(CompanyBase):
    """Schema for company creation."""
    name: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    
    @field_validator("slug", mode="before")
    def generate_slug(cls, v, info):
        if not v and "name" in info.data:
            # Generate slug from name if not provided
            slug = info.data["name"].lower()
            slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
            slug = "-".join(filter(None, slug.split("-")))
            return slug[:100]
        return v
    
    @field_validator("founded_year")
    def validate_founded_year(cls, v):
        if v and v > datetime.now().year:
            raise ValueError("Founded year cannot be in the future")
        return v


class CompanyUpdate(BaseModel):
    """Schema for company profile updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
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
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    facebook_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    skills_focus: Optional[List[str]] = None
    learning_goals: Optional[List[str]] = None
    billing_email: Optional[EmailStr] = None
    settings: Optional[Dict[str, Any]] = None
    
    @field_validator("founded_year")
    def validate_founded_year(cls, v):
        if v and v > datetime.now().year:
            raise ValueError("Founded year cannot be in the future")
        return v


# Response schemas  
class CompanyResponse(BaseModel):
    """Schema for company response data."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    logo_url: Optional[str]
    website: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    industry: Optional[IndustryType]
    company_size: Optional[CompanySize]
    founded_year: Optional[int]
    employee_count: Optional[int]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    facebook_url: Optional[str]
    github_url: Optional[str]
    skills_focus: List[str]
    learning_goals: List[str]
    subscription_plan: str
    subscription_status: str
    is_active: bool
    is_verified: bool
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CompanyPublicResponse(BaseModel):
    """Schema for public company profile data."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    logo_url: Optional[str]
    website: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    industry: Optional[IndustryType]
    company_size: Optional[CompanySize]
    founded_year: Optional[int]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    facebook_url: Optional[str]
    github_url: Optional[str]
    skills_focus: List[str]
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Team member schemas
class TeamMemberBase(BaseModel):
    """Base team member schema."""
    role: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    permissions: Optional[List[str]] = []


class TeamMemberInvite(TeamMemberBase):
    """Schema for inviting team members."""
    email: EmailStr
    message: Optional[str] = Field(None, max_length=500)


class TeamMemberUpdate(BaseModel):
    """Schema for updating team member details."""
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(BaseModel):
    """Schema for team member response data."""
    id: UUID
    company_id: UUID
    user_id: UUID
    role: str
    title: Optional[str]
    department: Optional[str]
    permissions: List[str]
    is_active: bool
    joined_at: datetime
    left_at: Optional[datetime]
    invited_by: Optional[UUID]
    invited_at: Optional[datetime]
    invitation_accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Subscription schemas
class SubscriptionPlan(BaseModel):
    """Schema for subscription plan information."""
    name: str
    price: float
    billing_cycle: str
    features: List[str]
    seats_included: int


class SubscriptionUpdate(BaseModel):
    """Schema for subscription updates."""
    plan_name: str = Field(..., min_length=1, max_length=100)
    billing_cycle: str = Field(..., pattern=r"^(monthly|yearly)$")
    seats_included: Optional[int] = Field(None, ge=1)


class SubscriptionResponse(BaseModel):
    """Schema for subscription response data."""
    id: UUID
    company_id: UUID
    plan_name: str
    plan_price: float
    billing_cycle: str
    currency: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    seats_included: int
    seats_used: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# List responses
class CompanyListResponse(BaseModel):
    """Schema for paginated company list response."""
    companies: List[CompanyResponse]
    total: int
    page: int
    size: int
    pages: int


class CompanyPublicListResponse(BaseModel):
    """Schema for paginated public company list response."""
    companies: List[CompanyPublicResponse]
    total: int
    page: int
    size: int
    pages: int


class TeamMemberListResponse(BaseModel):
    """Schema for paginated team member list response."""
    members: List[TeamMemberResponse]
    total: int
    page: int
    size: int
    pages: int


# Company verification schema
class CompanyVerificationRequest(BaseModel):
    """Schema for requesting company verification."""
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)
    business_documents: Optional[List[str]] = []  # URLs to uploaded documents
    additional_info: Optional[str] = Field(None, max_length=1000)


# Company search and filter schemas
class CompanySearchFilters(BaseModel):
    """Schema for company search and filtering."""
    industry: Optional[IndustryType] = None
    company_size: Optional[CompanySize] = None
    country: Optional[str] = None
    skills: Optional[List[str]] = []
    verified_only: bool = False
    active_only: bool = True