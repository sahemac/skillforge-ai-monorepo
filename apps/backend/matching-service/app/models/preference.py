"""
User preference models for SkillForge AI Matching Service
"""

from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship, JSON
from sqlalchemy import Column
from .base import BaseModel, PreferenceType


class UserPreference(BaseModel, table=True):
    """User preferences for matching algorithms."""

    __tablename__ = "user_preferences"

    # User identification
    user_id: str = Field(index=True, description="User ID from matching profile")
    profile_id: str = Field(index=True, description="Matching profile ID")

    # Preference details
    preference_type: str = Field(
        description="Type of preference (location, salary, skills, etc.)"
    )
    preference_name: str = Field(description="Human-readable preference name")
    preference_value: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        description="Structured preference value"
    )

    # Priority and weight
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Preference priority (1=highest, 10=lowest)"
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=10.0,
        description="Weight in matching algorithm"
    )

    # Constraints
    is_mandatory: bool = Field(
        default=False,
        description="Whether this preference is a hard constraint"
    )
    is_flexible: bool = Field(
        default=True,
        description="Whether this preference can be relaxed"
    )

    # Status
    is_active: bool = Field(default=True, description="Is preference active")

    # Metadata
    preference_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional preference metadata"
    )

    # Relationships
    profile: Optional["MatchingProfile"] = Relationship(
        back_populates="preferences",
        sa_relationship_kwargs={
            "foreign_keys": "[UserPreference.profile_id]",
            "primaryjoin": "UserPreference.profile_id == MatchingProfile.id"
        }
    )


class PreferenceHistory(BaseModel, table=True):
    """History of user preference changes."""

    __tablename__ = "preference_history"

    # Reference
    user_id: str = Field(index=True, description="User ID")
    preference_id: str = Field(index=True, description="Original preference ID")

    # Historical data
    old_value: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Previous preference value"
    )
    new_value: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        description="New preference value"
    )

    # Change tracking
    change_reason: Optional[str] = Field(
        default=None,
        description="Reason for preference change"
    )
    changed_by: Optional[str] = Field(
        default=None,
        description="Who/what made the change"
    )


class UserPreferenceCreate(SQLModel):
    """Schema for creating user preference."""

    user_id: str
    profile_id: str
    preference_type: str
    preference_name: str
    preference_value: Dict[str, Any]
    priority: int = 1
    weight: float = 1.0
    is_mandatory: bool = False
    is_flexible: bool = True
    is_active: bool = True
    preference_metadata: Optional[Dict[str, Any]] = None


class UserPreferenceUpdate(SQLModel):
    """Schema for updating user preference."""

    preference_name: Optional[str] = None
    preference_value: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    weight: Optional[float] = None
    is_mandatory: Optional[bool] = None
    is_flexible: Optional[bool] = None
    is_active: Optional[bool] = None
    preference_metadata: Optional[Dict[str, Any]] = None


class UserPreferenceResponse(SQLModel):
    """Response schema for user preference."""

    id: str
    user_id: str
    profile_id: str
    preference_type: str
    preference_name: str
    preference_value: Dict[str, Any]
    priority: int
    weight: float
    is_mandatory: bool
    is_flexible: bool
    is_active: bool
    preference_metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: Optional[str]


class PreferenceTemplate(SQLModel):
    """Template for common preference patterns."""

    template_name: str
    template_description: str
    preference_type: str
    default_value: Dict[str, Any]
    default_priority: int
    default_weight: float
    is_mandatory: bool
    validation_schema: Optional[Dict[str, Any]] = None


class BulkPreferenceUpdate(SQLModel):
    """Bulk update multiple preferences."""

    preferences: List[Dict[str, Any]]
    update_reason: Optional[str] = None
    validate_before_update: bool = True


class PreferenceStats(SQLModel):
    """Statistics about user preferences."""

    user_id: str
    total_preferences: int
    active_preferences: int
    mandatory_preferences: int
    preference_types: Dict[str, int]
    avg_priority: float
    avg_weight: float
    last_updated: Optional[str]