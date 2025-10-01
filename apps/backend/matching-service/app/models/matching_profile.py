"""
Matching profile models for SkillForge AI Matching Service
"""

from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON
from sqlalchemy import Column, Text, Float
from .base import BaseModel


class MatchingProfile(BaseModel, table=True):
    """User matching profile with preferences and embeddings."""

    __tablename__ = "matching_profiles"

    # User identification
    user_id: str = Field(index=True, description="User ID from user-service")
    user_type: str = Field(description="Type: learner, company, mentor")

    # Profile data
    profile_data: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        description="Complete user profile data"
    )

    # Skills and interests
    skills: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="User skills list"
    )
    interests: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="User interests and domains"
    )

    # Experience and preferences
    experience_level: Optional[str] = Field(
        default=None,
        description="beginner, intermediate, advanced, expert"
    )
    preferred_location: Optional[str] = Field(default=None)
    preferred_work_mode: Optional[str] = Field(
        default=None,
        description="remote, hybrid, onsite"
    )
    salary_expectations: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Salary range and currency"
    )

    # Embeddings for semantic search
    skills_embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Vector embedding for skills"
    )
    profile_embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Vector embedding for complete profile"
    )

    # Matching preferences
    matching_radius_km: Optional[float] = Field(
        default=50.0,
        description="Geographical matching radius in kilometers"
    )
    is_active: bool = Field(default=True, description="Profile active for matching")

    # Computed fields
    profile_completeness_score: float = Field(
        default=0.0,
        description="Profile completeness percentage (0.0-1.0)"
    )
    last_activity: Optional[str] = Field(
        default=None,
        description="Timestamp of last user activity"
    )

    # Relationships
    match_results: List["MatchResult"] = Relationship(
        back_populates="user_profile",
        sa_relationship_kwargs={"foreign_keys": "[MatchResult.user_id]"}
    )
    preferences: List["UserPreference"] = Relationship(back_populates="profile")


class MatchingProfileCreate(SQLModel):
    """Schema for creating matching profile."""

    user_id: str
    user_type: str
    profile_data: Dict[str, Any]
    skills: List[str] = []
    interests: List[str] = []
    experience_level: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_work_mode: Optional[str] = None
    salary_expectations: Optional[Dict[str, Any]] = None
    matching_radius_km: float = 50.0
    is_active: bool = True


class MatchingProfileUpdate(SQLModel):
    """Schema for updating matching profile."""

    profile_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    experience_level: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_work_mode: Optional[str] = None
    salary_expectations: Optional[Dict[str, Any]] = None
    matching_radius_km: Optional[float] = None
    is_active: Optional[bool] = None


class MatchingProfileResponse(SQLModel):
    """Response schema for matching profile."""

    id: str
    user_id: str
    user_type: str
    skills: List[str]
    interests: List[str]
    experience_level: Optional[str]
    preferred_location: Optional[str]
    preferred_work_mode: Optional[str]
    salary_expectations: Optional[Dict[str, Any]]
    matching_radius_km: float
    is_active: bool
    profile_completeness_score: float
    created_at: str
    updated_at: Optional[str]