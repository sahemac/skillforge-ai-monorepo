"""
Schemas package for SkillForge AI User Service
Pydantic models for request/response validation
"""

from .user import (
    # Base schemas
    UserBase,
    
    # Request schemas
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserRoleUpdate,
    UserStatusUpdate,
    UserLogin,
    UserRegister,
    
    # Response schemas
    UserResponse,
    UserPublicResponse,
    UserAdminResponse,
    UserListResponse,
    UserPublicListResponse,
    
    # Authentication schemas
    Token,
    TokenData,
    RefreshToken,
    
    # Email verification schemas
    EmailVerificationRequest,
    EmailVerificationConfirm,
    
    # Password reset schemas
    PasswordResetRequest,
    PasswordResetConfirm,
    
    # Settings schemas
    UserSettingsResponse,
    UserSettingsUpdate,
)

from .company import (
    # Base schemas
    CompanyBase,
    
    # Request schemas
    CompanyCreate,
    CompanyUpdate,
    
    # Response schemas
    CompanyResponse,
    CompanyPublicResponse,
    CompanyListResponse,
    CompanyPublicListResponse,
    
    # Team member schemas
    TeamMemberBase,
    TeamMemberInvite,
    TeamMemberUpdate,
    TeamMemberResponse,
    TeamMemberListResponse,
    
    # Subscription schemas
    SubscriptionPlan,
    SubscriptionUpdate,
    SubscriptionResponse,
    
    # Verification schemas
    CompanyVerificationRequest,
    
    # Search schemas
    CompanySearchFilters,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate", 
    "UserPasswordUpdate",
    "UserRoleUpdate",
    "UserStatusUpdate",
    "UserLogin",
    "UserRegister",
    "UserResponse",
    "UserPublicResponse", 
    "UserAdminResponse",
    "UserListResponse",
    "UserPublicListResponse",
    "Token",
    "TokenData",
    "RefreshToken",
    "EmailVerificationRequest",
    "EmailVerificationConfirm",
    "PasswordResetRequest", 
    "PasswordResetConfirm",
    "UserSettingsResponse",
    "UserSettingsUpdate",
    
    # Company schemas
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyPublicResponse",
    "CompanyListResponse",
    "CompanyPublicListResponse",
    "TeamMemberBase",
    "TeamMemberInvite",
    "TeamMemberUpdate", 
    "TeamMemberResponse",
    "TeamMemberListResponse",
    "SubscriptionPlan",
    "SubscriptionUpdate",
    "SubscriptionResponse",
    "CompanyVerificationRequest",
    "CompanySearchFilters",
]