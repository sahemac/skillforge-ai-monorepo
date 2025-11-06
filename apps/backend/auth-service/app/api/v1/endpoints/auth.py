"""
Authentication endpoints for SkillForge AI User Service
"""

from datetime import datetime, timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.api.dependencies import get_db, rate_limit_dependency, get_current_active_user
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
from app.models.user import User, UserStatus

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
        # Validate email format and DNS before proceeding
        from app.utils.email_validator import validate_email_format

        is_valid, validated_email_or_error = await validate_email_format(user_create.email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validated_email_or_error
            )

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

        # Send verification email asynchronously
        try:
            from app.utils.email import send_verification_email
            from app.core.security import create_email_verification_token

            verification_token = create_email_verification_token(user.email)
            email_sent, error_message = await send_verification_email(
                to_email=user.email,
                first_name=user.first_name or user.username,
                verification_token=verification_token,
                request=request
            )

            if email_sent:
                logger.info(f"✉ Verification email sent successfully to {user.email}")
            else:
                logger.warning(
                    f"⚠ Failed to send verification email to {user.email}: {error_message}"
                )
                # Don't block registration if email fails
                # User can request a new verification email later

        except Exception as email_error:
            logger.error(f"✗ Email verification error for {user.email}: {str(email_error)}")
            # Don't block registration on email failure

        logger.info(f"✓ New user registered: {user.email}")

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

        # CRITICAL: Block login if email is not verified
        if not user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your inbox and verify your email address before logging in."
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
                "is_verified": user.is_email_verified
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

        # Convert user to UserResponse
        from app.schemas.user import UserResponse
        user_response = UserResponse.model_validate(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "user": user_response
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
                "is_verified": user.is_email_verified
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
) -> Dict[str, str]:
    """Request email verification (resend)."""
    try:
        # Check if user exists
        user = await user_crud.get_by_email(db, request_data.email)
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, verification link has been sent"}

        # Check if already verified
        if user.is_email_verified:
            return {"message": "Email is already verified"}

        # Generate verification token
        verification_token = create_email_verification_token(user.email)

        # Send verification email with rate limiting
        from app.utils.email import send_verification_email

        email_sent, error_message = await send_verification_email(
            to_email=user.email,
            first_name=user.first_name or user.username,
            verification_token=verification_token,
            request=request
        )

        if not email_sent:
            logger.warning(f"Failed to resend verification email to {user.email}: {error_message}")
            # Still return success message for security
            return {"message": "If the email exists, verification link has been sent"}

        logger.info(f"Email verification resent: {user.email}")

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
        
        if user.is_email_verified:
            return {"message": "Email is already verified"}
        
        # Verify user
        await user_crud.verify_email(db, user)
        await db.commit()

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


# ============================================================================
# TWO-FACTOR AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/2fa/setup", response_model=dict)
async def setup_two_factor(
    password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Setup 2FA for current user."""
    try:
        from app.core.security import verify_password
        from app.crud import two_factor as two_factor_crud
        from app.utils.two_factor import generate_totp_secret, generate_qr_code

        # Verify password for security
        if not verify_password(password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )

        # Check if 2FA already exists
        existing_2fa = await two_factor_crud.get_by_user_id(db, current_user.id)
        if existing_2fa and existing_2fa.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )

        # Generate new secret
        secret = generate_totp_secret()

        # Create or update 2FA record
        if existing_2fa:
            await two_factor_crud.delete(db, existing_2fa)

        two_fa = await two_factor_crud.create(db, current_user.id, secret)

        # Generate QR code
        qr_code = generate_qr_code(secret, current_user.email)

        logger.info(f"2FA setup initiated for user: {current_user.email}")

        return {
            "secret": secret,
            "qr_code_url": qr_code,
            "backup_codes": two_fa.backup_codes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA setup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA setup failed"
        )


@router.post("/2fa/verify")
async def verify_two_factor(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Verify and enable 2FA."""
    try:
        from app.crud import two_factor as two_factor_crud
        from app.utils.two_factor import verify_totp_code

        # Get 2FA settings
        two_fa = await two_factor_crud.get_by_user_id(db, current_user.id)
        if not two_fa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="2FA not setup. Please setup 2FA first"
            )

        # Verify code
        if not verify_totp_code(two_fa.secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Enable 2FA
        await two_factor_crud.enable(db, two_fa)

        # Update user model
        current_user.two_factor_enabled = True
        await db.commit()

        logger.info(f"2FA enabled for user: {current_user.email}")

        return {"message": "2FA enabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA verification failed"
        )


@router.post("/2fa/disable")
async def disable_two_factor(
    password: str,
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Disable 2FA for current user."""
    try:
        from app.core.security import verify_password
        from app.crud import two_factor as two_factor_crud
        from app.utils.two_factor import verify_totp_code

        # Verify password
        if not verify_password(password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )

        # Get 2FA settings
        two_fa = await two_factor_crud.get_by_user_id(db, current_user.id)
        if not two_fa or not two_fa.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled"
            )

        # Verify 2FA code
        if not verify_totp_code(two_fa.secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )

        # Disable 2FA
        await two_factor_crud.disable(db, two_fa)

        # Update user model
        current_user.two_factor_enabled = False
        await db.commit()

        logger.info(f"2FA disabled for user: {current_user.email}")

        return {"message": "2FA disabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA disable error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA disable failed"
        )


@router.post("/2fa/login", response_model=Token)
async def login_with_two_factor(
    login_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
) -> Any:
    """Login with 2FA code."""
    try:
        from app.crud import two_factor as two_factor_crud
        from app.utils.two_factor import verify_totp_code

        email = login_data.get("email")
        password = login_data.get("password")
        code = login_data.get("code")
        remember_me = login_data.get("remember_me", False)

        # Authenticate user
        user = await user_crud.authenticate(db, email=email, password=password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if 2FA is enabled
        two_fa = await two_factor_crud.get_by_user_id(db, user.id)
        if not two_fa or not two_fa.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled for this account"
            )

        # Verify 2FA code or backup code
        code_valid = verify_totp_code(two_fa.secret, code)

        if not code_valid:
            # Try backup code
            code_valid = await two_factor_crud.verify_backup_code(db, two_fa, code)
            if code_valid:
                logger.info(f"Backup code used for login: {user.email}")

        if not code_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )

        # Update last verified
        await two_factor_crud.verify_and_update(db, two_fa)

        # Create tokens (same as regular login)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        if remember_me:
            access_token_expires = timedelta(hours=24)
            refresh_token_expires = timedelta(days=30)

        access_token = create_access_token(
            subject=user.id,
            expires_delta=access_token_expires,
            additional_claims={
                "email": user.email,
                "role": user.role.value,
                "is_verified": user.is_email_verified,
                "2fa_verified": True
            }
        )

        refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=refresh_token_expires
        )

        # Create session
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
                "remember_me": remember_me,
                "2fa_used": True
            }
        )

        logger.info(f"User logged in with 2FA: {user.email}")

        from app.schemas.auth import UserResponse
        user_response = UserResponse.model_validate(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "user": user_response
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA login failed"
        )


# ============================================================================
# PASSWORD CHANGE ENDPOINT
# ============================================================================

@router.post("/password/change")
async def change_password(
    password_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Change password for authenticated user."""
    try:
        from app.core.security import verify_password

        current_password = password_data.get("current_password")
        new_password = password_data.get("new_password")

        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Validate new password
        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )

        password_validation = validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['issues'])}"
            )

        # Update password
        await user_crud.update_password(db, current_user, new_password)

        # Logout from all sessions for security
        await session_crud.deactivate_user_sessions(db, current_user.id)

        logger.info(f"Password changed for user: {current_user.email}")

        return {"message": "Password changed successfully. Please login again."}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
