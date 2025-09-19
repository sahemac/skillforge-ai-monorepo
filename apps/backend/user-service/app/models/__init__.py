"""
Models package for SkillForge AI User Service
"""

from .base import TimestampMixin, UUIDMixin
# Utilisation des modèles définitifs
from .user import (
    User, 
    UserRole, 
    UserStatus,
    UserSkillLevel,
    UserSession,
    UserSettings
)
from .company import (
    CompanyProfile, 
    CompanySize, 
    IndustryType,
    TeamMember,
    Subscription
)

__all__ = [
    # Base mixins
    "TimestampMixin",
    "UUIDMixin",
    
    # User models
    "User",
    "UserRole",
    "UserStatus",
    "UserSkillLevel",
    "UserSession",
    "UserSettings",
    
    # Company models
    "CompanyProfile",
    "CompanySize",
    "IndustryType", 
    "TeamMember",
    "Subscription",
]