"""
Core package for SkillForge AI User Service
Configuration, database, security utilities
"""

from .config import Settings, get_settings
from .database import (
    get_session,
    get_db_transaction, 
    create_db_and_tables,
    check_db_connection,
    close_db_connection,
    reset_database,
    get_db_info,
    DatabaseTransaction
)
from .security import (
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    verify_token,
    verify_password,
    get_password_hash,
    generate_random_password,
    generate_api_key,
    Permissions,
    ROLE_PERMISSIONS,
    get_user_permissions,
    check_permission,
    add_security_headers,
    rate_limiter,
    sanitize_input,
    validate_email_format,
    validate_password_strength
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    
    # Database
    "get_session",
    "get_db_transaction",
    "create_db_and_tables",
    "check_db_connection", 
    "close_db_connection",
    "reset_database",
    "get_db_info",
    "DatabaseTransaction",
    
    # Security
    "create_access_token",
    "create_refresh_token", 
    "create_email_verification_token",
    "create_password_reset_token",
    "verify_token",
    "verify_password",
    "get_password_hash",
    "generate_random_password",
    "generate_api_key",
    "Permissions",
    "ROLE_PERMISSIONS",
    "get_user_permissions",
    "check_permission",
    "add_security_headers",
    "rate_limiter",
    "sanitize_input",
    "validate_email_format",
    "validate_password_strength",
]