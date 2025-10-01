"""
Models package for SkillForge AI Matching Service
"""

from .base import (
    BaseModel,
    TimestampMixin,
    UUIDMixin,
    MatchingStatus,
    MatchingType,
    PreferenceType,
)
from .matching_profile import (
    MatchingProfile,
    MatchingProfileCreate,
    MatchingProfileUpdate,
    MatchingProfileResponse,
)
from .match_result import (
    MatchResult,
    MatchResultCreate,
    MatchResultUpdate,
    MatchResultResponse,
    MatchBatch,
    MatchBatchResponse,
)
from .preference import (
    UserPreference,
    PreferenceHistory,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    PreferenceTemplate,
    BulkPreferenceUpdate,
    PreferenceStats,
)

__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "MatchingStatus",
    "MatchingType",
    "PreferenceType",
    # Matching Profile
    "MatchingProfile",
    "MatchingProfileCreate",
    "MatchingProfileUpdate",
    "MatchingProfileResponse",
    # Match Result
    "MatchResult",
    "MatchResultCreate",
    "MatchResultUpdate",
    "MatchResultResponse",
    "MatchBatch",
    "MatchBatchResponse",
    # Preferences
    "UserPreference",
    "PreferenceHistory",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",
    "PreferenceTemplate",
    "BulkPreferenceUpdate",
    "PreferenceStats",
]