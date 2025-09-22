"""
Models for SkillForge AI Company Service
"""

from .base import TimestampMixin, UUIDMixin
from .company import (
    CompanyProfile, 
    CompanyTeamMember, 
    CompanySubscription,
    CompanySize,
    IndustryType,
    TeamMember,  # Alias
    Subscription  # Alias
)

__all__ = [
    "TimestampMixin", "UUIDMixin",
    "CompanyProfile", "CompanyTeamMember", "CompanySubscription",
    "CompanySize", "IndustryType",
    "TeamMember", "Subscription"
]