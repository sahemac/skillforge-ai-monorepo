"""
API package for SkillForge AI User Service
"""

from .v1 import api_router
from .dependencies import (
    get_db,
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_current_superuser,
    get_current_admin_user,
    get_optional_current_user,
    require_permission,
    require_roles,
    get_pagination_params,
    get_search_params,
    PaginationParams,
    SearchParams
)

__all__ = [
    "api_router",
    "get_db",
    "get_current_user", 
    "get_current_active_user",
    "get_current_verified_user",
    "get_current_superuser",
    "get_current_admin_user",
    "get_optional_current_user",
    "require_permission",
    "require_roles",
    "get_pagination_params",
    "get_search_params",
    "PaginationParams",
    "SearchParams",
]