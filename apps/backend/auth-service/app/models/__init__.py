"""
Models package for SkillForge AI Auth Service
NOW USING SHARED MODELS - Single Source of Truth
"""

# Import all models from shared package (eliminates duplication)
from skillforge_models import (
    # Base classes
    Base,
    TimestampMixin,
    UUIDMixin,
    # User models (READ-ONLY for auth-service)
    User,
    UserRole,
    UserStatus,
    UserSkillLevel,
    UserSession,
    UserSettings,
    # 2FA models (READ/WRITE - owned by auth-service)
    UserTwoFactor,
)

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
    "UserSession",
    "UserSettings",
    # 2FA models
    "UserTwoFactor",
]
