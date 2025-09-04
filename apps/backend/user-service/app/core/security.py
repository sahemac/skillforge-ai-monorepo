"""
Security utilities for SkillForge AI User Service
JWT tokens, password hashing, permissions, etc.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from uuid import UUID
import jwt
from passlib.context import CryptContext
from passlib.handlers.bcrypt import bcrypt

from app.core.config import get_settings
from app.models.user_simple import UserRole

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, UUID], 
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32),  # JWT ID for token invalidation
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_email_verification_token(email: str) -> str:
    """Create token for email verification."""
    expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours expiry
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_password_reset_token(email: str) -> str:
    """Create token for password reset."""
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Check token type if specified
        if expected_type and payload.get("type") != expected_type:
            return None
        
        return payload
        
    except jwt.PyJWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def generate_random_password(length: int = 12) -> str:
    """Generate a random password."""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate an API key."""
    return f"sk_{secrets.token_urlsafe(32)}"


# Permission system
class Permissions:
    """Permission constants."""
    
    # User permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_ADMIN = "user:admin"
    
    # Company permissions
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    COMPANY_DELETE = "company:delete"
    COMPANY_ADMIN = "company:admin"
    
    # Team permissions
    TEAM_READ = "team:read"
    TEAM_WRITE = "team:write"
    TEAM_DELETE = "team:delete"
    TEAM_ADMIN = "team:admin"
    
    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_ADMIN = "system:admin"


# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.USER: [
        Permissions.USER_READ,
        Permissions.COMPANY_READ,
        Permissions.TEAM_READ,
    ],
    UserRole.MODERATOR: [
        Permissions.USER_READ,
        Permissions.USER_WRITE,
        Permissions.COMPANY_READ,
        Permissions.COMPANY_WRITE,
        Permissions.TEAM_READ,
        Permissions.TEAM_WRITE,
    ],
    UserRole.PREMIUM_USER: [
        Permissions.USER_READ,
        Permissions.USER_WRITE,
        Permissions.COMPANY_READ,
        Permissions.COMPANY_WRITE,
        Permissions.TEAM_READ,
        Permissions.TEAM_WRITE,
    ],
    UserRole.ADMIN: [
        Permissions.USER_READ,
        Permissions.USER_WRITE,
        Permissions.USER_DELETE,
        Permissions.USER_ADMIN,
        Permissions.COMPANY_READ,
        Permissions.COMPANY_WRITE,
        Permissions.COMPANY_DELETE,
        Permissions.COMPANY_ADMIN,
        Permissions.TEAM_READ,
        Permissions.TEAM_WRITE,
        Permissions.TEAM_DELETE,
        Permissions.TEAM_ADMIN,
        Permissions.SYSTEM_READ,
        Permissions.SYSTEM_WRITE,
        Permissions.SYSTEM_ADMIN,
    ],
}


def get_user_permissions(role: UserRole, is_superuser: bool = False) -> list[str]:
    """Get permissions for a user role."""
    if is_superuser:
        # Superuser has all permissions
        return list(vars(Permissions).values())
    
    return ROLE_PERMISSIONS.get(role, [])


def check_permission(user_role: UserRole, required_permission: str, is_superuser: bool = False) -> bool:
    """Check if user has required permission."""
    user_permissions = get_user_permissions(user_role, is_superuser)
    return required_permission in user_permissions


# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY", 
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    ),
}


def add_security_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Add security headers to response."""
    if not settings.is_development:
        headers.update(SECURITY_HEADERS)
    return headers


# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self._attempts = {}
        self._reset_times = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit."""
        now = datetime.utcnow()
        
        # Reset counter if window has passed
        if key in self._reset_times and now > self._reset_times[key]:
            self._attempts[key] = 0
            self._reset_times[key] = now + timedelta(seconds=window)
        
        # Initialize if not exists
        if key not in self._attempts:
            self._attempts[key] = 0
            self._reset_times[key] = now + timedelta(seconds=window)
        
        # Check limit
        if self._attempts[key] >= limit:
            return False
        
        # Increment counter
        self._attempts[key] += 1
        return True
    
    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining attempts."""
        current = self._attempts.get(key, 0)
        return max(0, limit - current)
    
    def reset(self, key: str) -> None:
        """Reset rate limit for key."""
        self._attempts.pop(key, None)
        self._reset_times.pop(key, None)


# Global rate limiter instance
rate_limiter = RateLimiter()


# Input validation and sanitization
def sanitize_input(value: str, max_length: int = 255) -> str:
    """Sanitize user input."""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove null bytes and control characters
    value = value.replace('\x00', '')
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
    
    # Truncate to max length
    return value[:max_length].strip()


def validate_email_format(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength."""
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter") 
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one number")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one special character")
    
    # Check for common passwords
    common_passwords = [
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "dragon", "password1"
    ]
    if password.lower() in common_passwords:
        issues.append("Password is too common")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "strength": "strong" if len(issues) == 0 else "weak"
    }