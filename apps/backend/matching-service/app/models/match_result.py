"""
Match result models for SkillForge AI Matching Service
"""

from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship, JSON
from sqlalchemy import Column, Text, Float, Integer
from .base import BaseModel, MatchingStatus, MatchingType


class MatchResult(BaseModel, table=True):
    """Results of matching algorithms with scores and metadata."""

    __tablename__ = "match_results"

    # Matching participants
    user_id: str = Field(index=True, description="Primary user ID")
    target_id: str = Field(index=True, description="Target user/project ID")
    target_type: str = Field(description="Type: user, project, job")

    # Matching algorithm info
    matching_type: str = Field(
        default=MatchingType.USER_TO_PROJECT,
        description="Type of matching algorithm used"
    )
    algorithm_version: str = Field(
        default="1.0.0",
        description="Version of matching algorithm"
    )

    # Scores and ranking
    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall matching score (0.0-1.0)"
    )
    skill_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Skills compatibility score"
    )
    experience_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Experience level compatibility"
    )
    location_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Location compatibility score"
    )
    preference_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="User preferences compatibility"
    )
    semantic_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Semantic similarity score"
    )

    # Ranking and confidence
    rank_position: Optional[int] = Field(
        default=None,
        description="Position in ranking (1-based)"
    )
    confidence_level: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Algorithm confidence in the match"
    )

    # Match details and reasoning
    match_reasons: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Reasons why this is a good match"
    )
    skill_overlaps: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Common skills between user and target"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Skills target has that user lacks"
    )

    # Metadata
    match_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional matching metadata"
    )
    computation_time_ms: Optional[float] = Field(
        default=None,
        description="Time taken to compute this match"
    )

    # Status and tracking
    status: str = Field(
        default=MatchingStatus.COMPLETED,
        description="Match computation status"
    )
    is_mutual: bool = Field(
        default=False,
        description="Whether the match is mutual (both parties match)"
    )
    user_feedback: Optional[str] = Field(
        default=None,
        description="User feedback on match quality"
    )
    feedback_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="User rating of match (1-5 stars)"
    )

    # Expiration and relevance
    expires_at: Optional[str] = Field(
        default=None,
        description="When this match expires"
    )
    is_active: bool = Field(default=True, description="Is match still valid")

    # Relationships
    user_profile: Optional["MatchingProfile"] = Relationship(
        back_populates="match_results",
        sa_relationship_kwargs={
            "foreign_keys": "[MatchResult.user_id]",
            "primaryjoin": "MatchResult.user_id == MatchingProfile.user_id"
        }
    )


class MatchResultCreate(SQLModel):
    """Schema for creating match result."""

    user_id: str
    target_id: str
    target_type: str
    matching_type: str = MatchingType.USER_TO_PROJECT
    algorithm_version: str = "1.0.0"
    overall_score: float
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    location_score: Optional[float] = None
    preference_score: Optional[float] = None
    semantic_score: Optional[float] = None
    rank_position: Optional[int] = None
    confidence_level: float = 0.0
    match_reasons: List[str] = []
    skill_overlaps: List[str] = []
    missing_skills: List[str] = []
    match_metadata: Dict[str, Any] = {}
    computation_time_ms: Optional[float] = None
    is_mutual: bool = False


class MatchResultUpdate(SQLModel):
    """Schema for updating match result."""

    overall_score: Optional[float] = None
    confidence_level: Optional[float] = None
    match_reasons: Optional[List[str]] = None
    match_metadata: Optional[Dict[str, Any]] = None
    user_feedback: Optional[str] = None
    feedback_score: Optional[int] = None
    is_active: Optional[bool] = None


class MatchResultResponse(SQLModel):
    """Response schema for match result."""

    id: str
    user_id: str
    target_id: str
    target_type: str
    matching_type: str
    overall_score: float
    skill_score: Optional[float]
    experience_score: Optional[float]
    location_score: Optional[float]
    preference_score: Optional[float]
    semantic_score: Optional[float]
    rank_position: Optional[int]
    confidence_level: float
    match_reasons: List[str]
    skill_overlaps: List[str]
    missing_skills: List[str]
    computation_time_ms: Optional[float]
    is_mutual: bool
    user_feedback: Optional[str]
    feedback_score: Optional[int]
    is_active: bool
    created_at: str
    updated_at: Optional[str]


class MatchBatch(SQLModel):
    """Batch matching request."""

    user_ids: List[str]
    target_ids: Optional[List[str]] = None
    matching_types: List[str] = [MatchingType.USER_TO_PROJECT]
    max_results_per_user: int = 10
    min_score_threshold: float = 0.0
    include_metadata: bool = True


class MatchBatchResponse(SQLModel):
    """Batch matching response."""

    total_matches: int
    processing_time_ms: float
    matches_by_user: Dict[str, List[MatchResultResponse]]
    summary: Dict[str, Any]