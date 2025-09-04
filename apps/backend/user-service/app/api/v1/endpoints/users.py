"""
User endpoints for SkillForge AI User Service
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from uuid import UUID

from app.api.dependencies import (
    get_db,
    get_current_active_user,
    get_current_verified_user,
    get_current_admin_user,
    get_pagination_params,
    get_search_params,
    PaginationParams,
    SearchParams
)
from app.crud import user as user_crud, user_settings as settings_crud
from app.schemas.user import (
    UserResponse,
    UserPublicResponse,
    UserAdminResponse,
    UserUpdate,
    UserPasswordUpdate,
    UserRoleUpdate,
    UserStatusUpdate,
    UserListResponse,
    UserPublicListResponse,
    UserSettingsResponse,
    UserSettingsUpdate
)
from app.models.user_simple import User, UserRole, UserStatus
from app.core.security import validate_password_strength, Permissions
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update current user's profile."""
    try:
        # Generate full name if first_name or last_name provided
        update_data = user_update.model_dump(exclude_unset=True)
        if "first_name" in update_data or "last_name" in update_data:
            first_name = update_data.get("first_name", current_user.first_name) or ""
            last_name = update_data.get("last_name", current_user.last_name) or ""
            update_data["full_name"] = f"{first_name} {last_name}".strip()
        
        updated_user = await user_crud.update(db, current_user, update_data)
        
        logger.info(f"User profile updated: {current_user.email}")
        
        return updated_user
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/me/change-password")
async def change_password(
    password_update: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Change current user's password."""
    try:
        # Verify current password
        from app.core.security import verify_password
        if not verify_password(password_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        password_validation = validate_password_strength(password_update.new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['issues'])}"
            )
        
        # Update password
        await user_crud.update_password(db, current_user, password_update.new_password)
        
        # Logout from all other sessions for security
        from app.crud import user_session
        await user_session.deactivate_user_sessions(db, current_user.id)
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user's settings."""
    settings = await settings_crud.get_by_user_id(db, current_user.id)
    if not settings:
        # Create default settings if they don't exist
        settings = await user_crud.create_default_settings(db, current_user.id)
    
    return settings


@router.put("/me/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update current user's settings."""
    try:
        update_data = settings_update.model_dump(exclude_unset=True)
        settings = await settings_crud.update_by_user_id(db, current_user.id, update_data)
        
        if not settings:
            # Create settings if they don't exist
            settings = await user_crud.create_default_settings(db, current_user.id)
            settings = await settings_crud.update(db, settings, update_data)
        
        logger.info(f"User settings updated: {current_user.email}")
        
        return settings
        
    except Exception as e:
        logger.error(f"Settings update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Settings update failed"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> None:
    """Delete current user account (soft delete)."""
    try:
        # Soft delete by deactivating account
        await user_crud.update_status(
            db, 
            current_user, 
            UserStatus.INACTIVE, 
            is_active=False
        )
        
        # Deactivate all sessions
        from app.crud import user_session
        await user_session.deactivate_user_sessions(db, current_user.id)
        
        logger.info(f"User account deleted: {current_user.email}")
        
    except Exception as e:
        logger.error(f"Account deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


# Public user endpoints
@router.get("/{user_id}/public", response_model=UserPublicResponse)
async def get_user_public_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user's public profile."""
    user = await user_crud.get(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/public", response_model=UserPublicListResponse)
async def get_public_users(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: SearchParams = Depends(get_search_params),
    verified_only: bool = Query(True, description="Show only verified users"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills")
) -> Any:
    """Get public user profiles with search and filtering."""
    try:
        filters = {"is_active": True, "status": UserStatus.ACTIVE}
        if verified_only:
            filters["is_verified"] = True
        
        if search.q:
            users = await user_crud.search_users(
                db,
                search_term=search.q,
                skip=pagination.skip,
                limit=pagination.limit,
                filters=filters
            )
        elif skills:
            users = await user_crud.get_users_by_skills(
                db,
                skills=skills,
                skip=pagination.skip,
                limit=pagination.limit
            )
        else:
            users = await user_crud.get_multi(
                db,
                skip=pagination.skip,
                limit=pagination.limit,
                filters=filters,
                order_by="created_at"
            )
        
        # Get total count
        total = await user_crud.count(db, filters=filters)
        total_pages = (total + pagination.size - 1) // pagination.size
        
        return {
            "users": users,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Public users list error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users list"
        )


# Admin endpoints
@router.get("/", response_model=UserListResponse)
async def get_users(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: SearchParams = Depends(get_search_params),
    current_user: User = Depends(get_current_admin_user),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
) -> Any:
    """Get all users (admin only)."""
    try:
        filters = {}
        if role:
            filters["role"] = role
        if status:
            filters["status"] = status
        if is_verified is not None:
            filters["is_verified"] = is_verified
        if is_active is not None:
            filters["is_active"] = is_active
        
        if search.q:
            users = await user_crud.search_users(
                db,
                search_term=search.q,
                skip=pagination.skip,
                limit=pagination.limit,
                filters=filters
            )
        else:
            order_by = search.sort_by or "created_at"
            if search.sort_order == "asc":
                order_by = order_by
            else:
                order_by = f"-{order_by}"
            
            users = await user_crud.get_multi(
                db,
                skip=pagination.skip,
                limit=pagination.limit,
                filters=filters,
                order_by=order_by
            )
        
        # Get total count
        total = await user_crud.count(db, filters=filters)
        total_pages = (total + pagination.size - 1) // pagination.size
        
        return {
            "users": users,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Admin users list error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users list"
        )


@router.get("/{user_id}", response_model=UserAdminResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Get user by ID (admin only)."""
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}/role", response_model=UserAdminResponse)
async def update_user_role(
    user_id: UUID,
    role_update: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Update user role (admin only)."""
    try:
        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent changing own role unless superuser
        if user_id == current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        
        updated_user = await user_crud.update_role(
            db, 
            user, 
            role_update.role,
            role_update.is_superuser
        )
        
        logger.info(f"User role updated: {user.email} -> {role_update.role}")
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Role update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role update failed"
        )


@router.put("/{user_id}/status", response_model=UserAdminResponse)
async def update_user_status(
    user_id: UUID,
    status_update: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Update user status (admin only)."""
    try:
        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent changing own status unless superuser
        if user_id == current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own status"
            )
        
        updated_user = await user_crud.update_status(
            db,
            user,
            status_update.status,
            status_update.is_active
        )
        
        # If user is being deactivated, logout all sessions
        if status_update.is_active is False or status_update.status == UserStatus.SUSPENDED:
            from app.crud import user_session
            await user_session.deactivate_user_sessions(db, user.id)
        
        logger.info(f"User status updated: {user.email} -> {status_update.status}")
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status update failed"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> None:
    """Delete user (admin only)."""
    try:
        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deleting own account unless superuser
        if user_id == current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Soft delete
        await user_crud.update_status(
            db,
            user,
            UserStatus.INACTIVE,
            is_active=False
        )
        
        # Deactivate all sessions
        from app.crud import user_session
        await user_session.deactivate_user_sessions(db, user.id)
        
        logger.info(f"User deleted: {user.email}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )