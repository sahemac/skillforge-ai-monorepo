"""
Authentication endpoints for SkillForge AI User Service
"""

from datetime import datetime, timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.api.dependencies import get_db, rate_limit_dependency
from app.crud import user as user_crud, user_session as session_crud
from app.schemas.user import (
    UserLogin,
    UserRegister, 
    Token,
    RefreshToken,
    UserResponse,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    PasswordResetRequest,
    PasswordResetConfirm
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    verify_token,
    validate_password_strength
)
from app.core.config import get_settings
from app.models.user_simple import UserStatus

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
) -> Any:
    """Register new user."""
    try:
        # Check if user already exists
        existing_user = await user_crud.get_by_email(db, user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Check username availability
        existing_username = await user_crud.get_by_username(db, user_create.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Validate password strength
        password_validation = validate_password_strength(user_create.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['issues'])}"
            )
        
        # Create user
        user = await user_crud.create(db, user_create)
        
        # Send verification email (in a real app, this would be done asynchronously)
        # await send_verification_email(user.email, user.first_name)
        
        logger.info(f"New user registered: {user.email}")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
) -> Any:
    """Login user and return JWT tokens."""
    try:
        # Authenticate user
        user = await user_crud.authenticate(
            db,
            email=user_credentials.email,
            password=user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Extended expiry for "remember me"
        if user_credentials.remember_me:
            access_token_expires = timedelta(hours=24)
            refresh_token_expires = timedelta(days=30)
        
        access_token = create_access_token(
            subject=user.id,
            expires_delta=access_token_expires,
            additional_claims={
                "email": user.email,
                "role": user.role.value,
                "is_verified": user.is_verified
            }
        )
        
        refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=refresh_token_expires
        )
        
        # Create session record
        session_expires = datetime.utcnow() + access_token_expires
        await session_crud.create_session(
            db,
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=session_expires,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            device_info={
                "ip": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
                "remember_me": user_credentials.remember_me
            }
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, expected_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        from uuid import UUID
        user_id = UUID(payload.get("sub"))
        user = await user_crud.get(db, user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Verify session exists and is active
        session = await session_crud.get_by_refresh_token(db, refresh_data.refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            subject=user.id,
            expires_delta=access_token_expires,
            additional_claims={
                "email": user.email,
                "role": user.role.value,
                "is_verified": user.is_verified
            }
        )
        
        new_refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=refresh_token_expires
        )
        
        # Update session
        await session_crud.update(
            db,
            session,
            {
                "session_token": access_token,
                "refresh_token": new_refresh_token,
                "expires_at": datetime.utcnow() + access_token_expires,
                "last_accessed_at": datetime.utcnow()
            }
        )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials=Depends(security)
) -> Dict[str, str]:
    """Logout user and invalidate session."""
    try:
        # Get token from authorization header
        token = credentials.credentials
        
        # Verify token and get user
        payload = verify_token(token, expected_type="access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get and deactivate session
        session = await session_crud.get_by_token(db, token)
        if session:
            await session_crud.deactivate_session(db, session)
            logger.info(f"User logged out: session {session.id}")
        
        return {"message": "Successfully logged out"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/logout-all")
async def logout_all(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials=Depends(security)
) -> Dict[str, str]:
    """Logout user from all sessions."""
    try:
        # Get token from authorization header
        token = credentials.credentials
        
        # Verify token and get user
        payload = verify_token(token, expected_type="access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        from uuid import UUID
        user_id = UUID(payload.get("sub"))
        
        # Deactivate all user sessions
        sessions_count = await session_crud.deactivate_user_sessions(db, user_id)
        
        logger.info(f"User logged out from all sessions: {user_id} ({sessions_count} sessions)")
        
        return {"message": f"Successfully logged out from {sessions_count} sessions"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout all error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout all failed"
        )


@router.post("/verify-email-request")
async def request_email_verification(
    request_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
) -> Dict[str, str]:
    """Request email verification."""
    try:
        # Check if user exists
        user = await user_crud.get_by_email(db, request_data.email)
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, verification link has been sent"}
        
        # Check if already verified
        if user.is_verified:
            return {"message": "Email is already verified"}
        
        # Generate verification token
        verification_token = create_email_verification_token(user.email)
        
        # In a real app, send email asynchronously
        # await send_verification_email(user.email, verification_token)
        
        logger.info(f"Email verification requested: {user.email}")
        
        return {"message": "If the email exists, verification link has been sent"}
        
    except Exception as e:
        logger.error(f"Email verification request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification request failed"
        )


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Verify email with token."""
    try:
        # Verify token
        payload = verify_token(verification_data.token, expected_type="email_verification")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        email = payload.get("sub")
        user = await user_crud.get_by_email(db, email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            return {"message": "Email is already verified"}
        
        # Verify user
        await user_crud.verify_email(db, user)
        
        logger.info(f"Email verified: {user.email}")
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/password-reset-request")
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
) -> Dict[str, str]:
    """Request password reset."""
    try:
        # Check if user exists
        user = await user_crud.get_by_email(db, request_data.email)
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, password reset link has been sent"}
        
        # Generate reset token
        reset_token = create_password_reset_token(user.email)
        
        # In a real app, send email asynchronously
        # await send_password_reset_email(user.email, reset_token)
        
        logger.info(f"Password reset requested: {user.email}")
        
        return {"message": "If the email exists, password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Confirm password reset with token."""
    try:
        # Verify token
        payload = verify_token(reset_data.token, expected_type="password_reset")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Validate new password
        password_validation = validate_password_strength(reset_data.new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['issues'])}"
            )
        
        email = payload.get("sub")
        user = await user_crud.get_by_email(db, email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        await user_crud.update_password(db, user, reset_data.new_password)
        
        # Logout user from all sessions for security
        await session_crud.deactivate_user_sessions(db, user.id)
        
        logger.info(f"Password reset completed: {user.email}")
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )