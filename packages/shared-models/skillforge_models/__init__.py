"""
SkillForge AI Shared Models
Single source of truth for database models across all microservices.
"""

from .base import Base, TimestampMixin, UUIDMixin
from .user import (
    User,
    UserRole,
    UserStatus,
    UserSkillLevel,
    UserSettings,
    UserSession,
)
from .two_factor import UserTwoFactor

__all__ = [
    # Base classes
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # User models
    "User",
    "UserRole",
    "UserStatus",
    "UserSkillLevel",
    "UserSettings",
    "UserSession",
    # Two-factor auth models
    "UserTwoFactor",
]

__version__ = "1.0.0"
