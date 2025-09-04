"""
Database configuration and session management for SkillForge AI User Service
"""

import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import logging

from app.core.config import get_settings
from app.models.base import SQLModel

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine
engine: Optional[AsyncEngine] = None


def create_engine() -> AsyncEngine:
    """Create database engine."""
    # Use separate parameters to avoid issues with @ in password
    database_url = (
        f"postgresql+asyncpg://"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )
    
    return create_async_engine(
        database_url,
        echo=settings.is_development and not settings.is_testing,
        future=True,
        poolclass=NullPool if settings.is_testing else None,
        pool_pre_ping=True,
        pool_recycle=300,  # 5 minutes
        json_serializer=None,  # Use default JSON serializer
        # Use separate connection parameters to avoid URL parsing issues
        connect_args={
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB,
            "command_timeout": 10,
        }
    )


def get_engine() -> AsyncEngine:
    """Get database engine."""
    global engine
    if engine is None:
        engine = create_engine()
    return engine


# Create session factory
SessionLocal = async_sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_and_tables() -> None:
    """Create database tables."""
    try:
        # Import all models to ensure they are registered with SQLModel
        from app.models import (
            User, 
            UserSettings, 
            UserSession,
            CompanyProfile, 
            TeamMember, 
            Subscription
        )
        
        engine = get_engine()
        
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Database tables created successfully")
        
        # Create first superuser if specified
        await create_first_superuser()
        
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


async def create_first_superuser() -> None:
    """Create first superuser if specified in settings."""
    if not settings.FIRST_SUPERUSER or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.info("No first superuser configuration found, skipping...")
        return
    
    try:
        from app.crud import user as user_crud
        from app.schemas import UserCreate
        from app.models import UserRole, UserStatus
        
        async with SessionLocal() as session:
            # Check if superuser already exists
            existing_user = await user_crud.get_by_email(session, settings.FIRST_SUPERUSER)
            if existing_user:
                logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists")
                return
            
            # Create superuser
            user_create = UserCreate(
                email=settings.FIRST_SUPERUSER,
                username="admin",
                password=settings.FIRST_SUPERUSER_PASSWORD,
                confirm_password=settings.FIRST_SUPERUSER_PASSWORD,
                first_name="Admin",
                last_name="User",
                terms_accepted=True,
                privacy_policy_accepted=True
            )
            
            # Create the user
            new_user = await user_crud.create(session, user_create)
            
            # Set as superuser and verify
            await user_crud.update_role(
                session, 
                new_user, 
                UserRole.ADMIN, 
                is_superuser=True
            )
            await user_crud.update_status(
                session,
                new_user,
                UserStatus.ACTIVE,
                is_active=True
            )
            await user_crud.verify_email(session, new_user)
            
            logger.info(f"First superuser created: {settings.FIRST_SUPERUSER}")
            
    except Exception as e:
        logger.error(f"Error creating first superuser: {str(e)}")
        # Don't raise here as this is not critical for app startup


async def check_db_connection() -> bool:
    """Check database connection health."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


async def close_db_connection() -> None:
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        engine = None
        logger.info("Database connections closed")


# Database utilities
async def reset_database() -> None:
    """Reset database (for testing only)."""
    if not settings.is_testing:
        raise RuntimeError("Database reset is only allowed in testing environment")
    
    try:
        from app.models import (
            User, 
            UserSettings, 
            UserSession,
            CompanyProfile, 
            TeamMember, 
            Subscription
        )
        
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("Database reset completed")
        
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise


async def run_migrations() -> None:
    """Run database migrations using Alembic."""
    try:
        from alembic.config import Config
        from alembic import command
        import os
        
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to reach the project root
        project_root = os.path.dirname(os.path.dirname(current_dir))
        alembic_cfg_path = os.path.join(project_root, "alembic.ini")
        
        if os.path.exists(alembic_cfg_path):
            alembic_cfg = Config(alembic_cfg_path)
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed")
        else:
            logger.warning("Alembic configuration not found, skipping migrations")
            
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        # Don't raise here as we fall back to create_all


# Database health check endpoint data
async def get_db_info() -> dict:
    """Get database information for health checks."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            # Get connection pool info
            pool = engine.pool
            pool_info = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }
            
            return {
                "status": "healthy",
                "version": version,
                "pool_info": pool_info,
                "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "hidden"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "hidden"
        }


# Context managers for database transactions
class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self) -> AsyncSession:
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            await self.session.commit()


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with transaction management."""
    async with SessionLocal() as session:
        async with DatabaseTransaction(session):
            try:
                yield session
            except Exception as e:
                logger.error(f"Database transaction error: {str(e)}")
                raise