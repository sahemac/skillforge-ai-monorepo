"""
CRUD package for SkillForge AI User Service
"""

from .base import CRUDBase
from .user import CRUDUser, CRUDUserSession, CRUDUserSettings, user, user_session, user_settings
from .company import CRUDCompany, CRUDTeamMember, CRUDSubscription, company, team_member, subscription

__all__ = [
    # Base CRUD
    "CRUDBase",
    
    # User CRUD classes
    "CRUDUser",
    "CRUDUserSession", 
    "CRUDUserSettings",
    
    # Company CRUD classes
    "CRUDCompany",
    "CRUDTeamMember",
    "CRUDSubscription",
    
    # CRUD instances
    "user",
    "user_session",
    "user_settings",
    "company",
    "team_member",
    "subscription",
]