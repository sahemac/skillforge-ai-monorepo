"""
User CRUD operations for SkillForge AI User Service
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.user_simple import User, UserSession, UserSettings, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Generate full name
        full_name = None
        if obj_in.first_name or obj_in.last_name:
            full_name = f"{obj_in.first_name or ''} {obj_in.last_name or ''}".strip()
        
        # Prepare user data
        user_data = obj_in.model_dump(exclude={"password", "confirm_password"})
        user_data.update({
            "hashed_password": get_password_hash(obj_in.password),
            "full_name": full_name,
            "terms_accepted_at": datetime.utcnow(),
            "privacy_policy_accepted_at": datetime.utcnow(),
        })
        
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # Create default user settings
        await self.create_default_settings(db, db_user.id)
        
        return db_user
    
    async def authenticate(
        self, 
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_by_email(db, email)
        if not user:
            return None
        
        # Check if account is locked
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            return None
        
        # Check password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            await self.increment_failed_login_attempts(db, user)
            return None
        
        # Reset failed login attempts and update last login
        await self.reset_failed_login_attempts(db, user)
        await self.update_last_login(db, user)
        
        return user
    
    async def update_password(
        self, 
        db: AsyncSession, 
        user: User, 
        new_password: str
    ) -> User:
        """Update user password."""
        hashed_password = get_password_hash(new_password)
        return await self.update(
            db, 
            user, 
            {"hashed_password": hashed_password}
        )
    
    async def verify_email(self, db: AsyncSession, user: User) -> User:
        """Mark user email as verified."""
        return await self.update(
            db,
            user,
            {
                "is_verified": True,
                "email_verified_at": datetime.utcnow(),
                "status": UserStatus.ACTIVE
            }
        )
    
    async def update_last_login(self, db: AsyncSession, user: User) -> User:
        """Update user's last login timestamp."""
        return await self.update(
            db,
            user,
            {"last_login_at": datetime.utcnow()}
        )
    
    async def increment_failed_login_attempts(
        self, 
        db: AsyncSession, 
        user: User
    ) -> User:
        """Increment failed login attempts and lock account if necessary."""
        failed_attempts = user.failed_login_attempts + 1
        update_data = {"failed_login_attempts": failed_attempts}
        
        # Lock account after 5 failed attempts for 30 minutes
        if failed_attempts >= 5:
            update_data["account_locked_until"] = datetime.utcnow() + timedelta(minutes=30)
        
        return await self.update(db, user, update_data)
    
    async def reset_failed_login_attempts(
        self, 
        db: AsyncSession, 
        user: User
    ) -> User:
        """Reset failed login attempts."""
        return await self.update(
            db,
            user,
            {
                "failed_login_attempts": 0,
                "account_locked_until": None
            }
        )
    
    async def update_role(
        self, 
        db: AsyncSession, 
        user: User, 
        role: UserRole,
        is_superuser: Optional[bool] = None
    ) -> User:
        """Update user role and superuser status."""
        update_data = {"role": role}
        if is_superuser is not None:
            update_data["is_superuser"] = is_superuser
        
        return await self.update(db, user, update_data)
    
    async def update_status(
        self, 
        db: AsyncSession, 
        user: User, 
        status: UserStatus,
        is_active: Optional[bool] = None
    ) -> User:
        """Update user status."""
        update_data = {"status": status}
        if is_active is not None:
            update_data["is_active"] = is_active
        
        return await self.update(db, user, update_data)
    
    async def activate_premium(
        self, 
        db: AsyncSession, 
        user: User,
        expires_at: datetime
    ) -> User:
        """Activate premium subscription for user."""
        return await self.update(
            db,
            user,
            {
                "is_premium": True,
                "premium_expires_at": expires_at
            }
        )
    
    async def deactivate_premium(self, db: AsyncSession, user: User) -> User:
        """Deactivate premium subscription for user."""
        return await self.update(
            db,
            user,
            {
                "is_premium": False,
                "premium_expires_at": None
            }
        )
    
    async def get_active_users(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get active users."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"is_active": True, "status": UserStatus.ACTIVE}
        )
    
    async def get_premium_users(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get premium users."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"is_premium": True, "is_active": True}
        )
    
    async def search_users(
        self,
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """Search users by name, username, or email."""
        search_fields = ["first_name", "last_name", "username", "email"]
        return await self.search(
            db,
            search_term,
            search_fields,
            skip=skip,
            limit=limit,
            filters=filters
        )
    
    async def get_users_by_skills(
        self,
        db: AsyncSession,
        skills: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by skills."""
        query = select(User).where(
            and_(
                User.is_active.is_(True),
                User.status == UserStatus.ACTIVE,
                User.skills.op("&&")(skills)  # PostgreSQL array overlap operator
            )
        ).offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_default_settings(
        self, 
        db: AsyncSession, 
        user_id: UUID
    ) -> UserSettings:
        """Create default settings for a new user."""
        settings_data = {
            "user_id": user_id,
            "theme": "light",
            "language": "en",
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "profile_visibility": "public",
            "show_email": False,
            "show_phone": False,
            "learning_reminders": True,
            "weekly_digest": True,
            "skill_recommendations": True,
            "custom_settings": {}
        }
        
        db_settings = UserSettings(**settings_data)
        db.add(db_settings)
        await db.commit()
        await db.refresh(db_settings)
        
        return db_settings


class CRUDUserSession(CRUDBase[UserSession, dict, dict]):
    """CRUD operations for UserSession model."""
    
    async def create_session(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_token: str,
        refresh_token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> UserSession:
        """Create a new user session."""
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device_info": device_info or {},
            "last_accessed_at": datetime.utcnow(),
            "is_active": True
        }
        
        return await self.create(db, session_data)
    
    async def get_by_token(
        self, 
        db: AsyncSession, 
        session_token: str
    ) -> Optional[UserSession]:
        """Get session by token."""
        result = await db.execute(
            select(UserSession).where(
                and_(
                    UserSession.session_token == session_token,
                    UserSession.is_active.is_(True),
                    UserSession.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_refresh_token(
        self, 
        db: AsyncSession, 
        refresh_token: str
    ) -> Optional[UserSession]:
        """Get session by refresh token."""
        result = await db.execute(
            select(UserSession).where(
                and_(
                    UserSession.refresh_token == refresh_token,
                    UserSession.is_active.is_(True)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_last_accessed(
        self, 
        db: AsyncSession, 
        session: UserSession
    ) -> UserSession:
        """Update session last accessed timestamp."""
        return await self.update(
            db,
            session,
            {"last_accessed_at": datetime.utcnow()}
        )
    
    async def deactivate_session(
        self, 
        db: AsyncSession, 
        session: UserSession
    ) -> UserSession:
        """Deactivate a session."""
        return await self.update(
            db,
            session,
            {
                "is_active": False,
                "logout_at": datetime.utcnow()
            }
        )
    
    async def deactivate_user_sessions(
        self, 
        db: AsyncSession, 
        user_id: UUID
    ) -> int:
        """Deactivate all sessions for a user."""
        from sqlalchemy import update
        
        result = await db.execute(
            update(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active.is_(True)
                )
            ).values(
                is_active=False,
                logout_at=datetime.utcnow()
            )
        )
        await db.commit()
        return result.rowcount
    
    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """Clean up expired sessions."""
        from sqlalchemy import delete
        
        result = await db.execute(
            delete(UserSession).where(
                UserSession.expires_at <= datetime.utcnow()
            )
        )
        await db.commit()
        return result.rowcount


class CRUDUserSettings(CRUDBase[UserSettings, dict, dict]):
    """CRUD operations for UserSettings model."""
    
    async def get_by_user_id(
        self, 
        db: AsyncSession, 
        user_id: UUID
    ) -> Optional[UserSettings]:
        """Get user settings by user ID."""
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
        settings_update: Dict[str, Any]
    ) -> Optional[UserSettings]:
        """Update user settings by user ID."""
        settings = await self.get_by_user_id(db, user_id)
        if settings:
            return await self.update(db, settings, settings_update)
        return None


# Create CRUD instances
user = CRUDUser(User)
user_session = CRUDUserSession(UserSession)
user_settings = CRUDUserSettings(UserSettings)