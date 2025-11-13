"""
Models package for SkillForge AI Auth Service
Re-exports from shared-models package
"""

# Import from shared-models package
from skillforge_models import (
    # Base classes
    TimestampMixin,
    UUIDMixin,
    # User models (read-only)
    User,
    UserRole,
    UserStatus,
    UserSkillLevel,
    UserSession,
    UserSettings,
    # Two-factor models (owned by auth-service)
    UserTwoFactor,
)

__all__ = [
    # Base mixins
    "TimestampMixin",
    "UUIDMixin",

    # User models (read-only)
    "User",
    "UserRole",
    "UserStatus",
    "UserSkillLevel",
    "UserSession",
    "UserSettings",

    # Two-factor models (owned by auth-service)
    "UserTwoFactor",
]
