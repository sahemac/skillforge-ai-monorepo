"""
Models package for SkillForge AI User Service
"""

from .base import TimestampMixin, UUIDMixin
# Utilisation du modèle User simplifié temporairement
from .user_simple import (
    User, 
    UserRole, 
    UserStatus,
    UserSkillLevel,
    UserSession,
    UserSettings,
    UserCreate,
    UserRead,
    UserUpdate
)
from .company_simple import (
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
    
    # User models (simplified)
    "User",
    "UserRole",
    "UserStatus",
    "UserSkillLevel",
    "UserSession",
    "UserSettings", 
    "UserCreate",
    "UserRead", 
    "UserUpdate",
    
    # Company models (simplified)
    "CompanyProfile",
    "CompanySize",
    "IndustryType", 
    "TeamMember",
    "Subscription",
]