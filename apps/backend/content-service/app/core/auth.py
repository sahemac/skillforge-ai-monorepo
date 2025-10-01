"""
Authentication utilities for Content Service
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import httpx
from ..core.config import get_settings

security = HTTPBearer()
settings = get_settings()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    Validates token with user-service.
    """
    try:
        token = credentials.credentials

        # Decode JWT locally first for basic validation
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}  # We'll verify with user-service
            )
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user_id"
                )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )

        # Verify token with user-service
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = await client.get(
                    f"{settings.USER_SERVICE_URL}/api/v1/auth/verify",
                    headers=headers,
                    timeout=10.0
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token verification failed"
                    )

                user_data = response.json()
                return {
                    "user_id": user_data.get("user_id", user_id),
                    "email": user_data.get("email"),
                    "role": user_data.get("role", "learner"),
                    "permissions": user_data.get("permissions", [])
                }

            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="User service unavailable"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to verify token with user service"
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, None otherwise.
    Used for endpoints that work both with and without authentication.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_permission(permission: str):
    """
    Decorator to require specific permission for endpoint access.
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        user_role = current_user.get("role", "learner")

        # Admin has all permissions
        if user_role == "admin":
            return current_user

        # Check specific permission
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required permission '{permission}' not granted"
            )

        return current_user

    return permission_checker


def require_role(role: str):
    """
    Decorator to require specific role for endpoint access.
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "learner")

        if user_role != role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role '{role}' not matched"
            )

        return current_user

    return role_checker


# Permission constants
class Permissions:
    CONTENT_CREATE = "content:create"
    CONTENT_READ = "content:read"
    CONTENT_UPDATE = "content:update"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"
    CONTENT_MODERATE = "content:moderate"
    ANALYTICS_VIEW = "analytics:view"
    COLLECTION_MANAGE = "collection:manage"