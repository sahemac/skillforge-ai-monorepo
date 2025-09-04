"""
Dependencies for SkillForge AI User Service API
Authentication, permissions, database sessions, etc.
"""

from typing import Optional, Generator, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.core.database import get_session
from app.core.security import verify_token, check_permission
from app.crud import user as user_crud
from app.models.user_simple import User, UserRole
from app.schemas.user import TokenData

logger = logging.getLogger(__name__)

# HTTP Bearer token security
security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """Get database session."""
    async for session in get_session():
        yield session


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Extract and verify JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token, expected_type="access")
        
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        return payload
        
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_data: Dict[str, Any] = Depends(get_current_user_token)
) -> User:
    """Get current authenticated user."""
    try:
        user_id = UUID(token_data.get("sub"))
        user = await user_crud.get(db, user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        # Update last accessed time for session tracking
        # This could be done asynchronously to avoid blocking the request
        
        return user
        
    except ValueError as e:
        logger.error(f"Invalid user ID in token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if current_user.role != UserRole.ADMIN and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_permission(permission: str):
    """Dependency factory for permission checking."""
    async def permission_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not check_permission(current_user.role, permission, current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    
    return permission_dependency


def require_roles(*roles: UserRole):
    """Dependency factory for role checking."""
    async def role_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {', '.join([role.value for role in roles])}"
            )
        return current_user
    
    return role_dependency


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token, expected_type="access")
        
        if payload is None:
            return None
        
        user_id = UUID(payload.get("sub"))
        user = await user_crud.get(db, user_id)
        
        if user and user.is_active:
            return user
            
    except Exception as e:
        logger.warning(f"Optional auth failed: {str(e)}")
        
    return None


# Rate limiting dependency
async def rate_limit_dependency(
    request: Request,
    limit: int = 60,  # requests per minute
    window: int = 60   # window in seconds
):
    """Rate limiting dependency."""
    from app.core.security import rate_limiter
    
    # Use client IP as key
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    if not rate_limiter.is_allowed(key, limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": str(window),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(0),
            }
        )


# Pagination dependency
class PaginationParams:
    """Pagination parameters."""
    
    def __init__(
        self, 
        page: int = 1,
        size: int = 20,
        max_size: int = 100
    ):
        if page < 1:
            page = 1
        if size < 1:
            size = 1
        if size > max_size:
            size = max_size
            
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


async def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(page=page, size=size)


# Company access dependency
async def get_user_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Check if user has access to company."""
    from app.crud import company as company_crud, team_member
    
    # Check if user owns the company
    company = await company_crud.get(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if company.owner_id == current_user.id:
        return company
    
    # Check if user is a team member
    membership = await team_member.get_by_company_and_user(
        db, company_id, current_user.id
    )
    
    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to company denied"
        )
    
    return company


# Search and filter dependencies
class SearchParams:
    """Search parameters."""
    
    def __init__(
        self,
        q: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None
    ):
        self.q = q
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "desc"
        self.filters = filters or {}
        
        # Validate sort order
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"


async def get_search_params(
    q: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> SearchParams:
    """Get search parameters."""
    return SearchParams(q=q, sort_by=sort_by, sort_order=sort_order)


# Request logging dependency
async def log_request(request: Request):
    """Log incoming requests."""
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Client: {request.client.host} - "
        f"User-Agent: {request.headers.get('user-agent', 'Unknown')}"
    )


# Content type validation
async def validate_json_content_type(request: Request):
    """Validate JSON content type for POST/PUT requests."""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Content-Type must be application/json"
            )


# Security headers dependency
async def add_security_headers_dependency(request: Request, call_next):
    """Add security headers to responses."""
    from app.core.security import add_security_headers
    
    response = await call_next(request)
    
    # Add security headers
    headers = dict(response.headers)
    headers = add_security_headers(headers)
    
    for key, value in headers.items():
        response.headers[key] = value
    
    return response