"""
Database configuration and session management for SkillForge AI Company Service
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.models.base import SQLModel

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine
engine: Optional[AsyncEngine] = None


def create_engine() -> AsyncEngine:
    """Create database engine."""
    # Build database URL from settings
    if settings.DATABASE_URL:
        database_url = settings.DATABASE_URL
    else:
        # Build from individual components
        user = settings.POSTGRES_USER
        password = settings.POSTGRES_PASSWORD
        host = settings.POSTGRES_HOST
        port = settings.POSTGRES_PORT
        db = settings.POSTGRES_DB
        
        if not password or not user:
            raise ValueError("Database credentials not provided")
        
        database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    # PostgreSQL configuration with Cloud SQL Proxy support
    connect_args = {}
    
    # Configuration for Cloud SQL Proxy
    if "localhost:5432" in database_url:
        connect_args = {
            "ssl": False,  # Disable SSL for cloud_sql_proxy
            "server_settings": {
                "application_name": "SkillForge_Company_Service"
            },
            "command_timeout": 30
        }
    
    return create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        poolclass=NullPool if getattr(settings, 'is_testing', False) else None,
        pool_pre_ping=True,
        pool_recycle=300,  # 5 minutes
        json_serializer=None,  # Use default JSON serializer
        connect_args=connect_args
    )


def get_engine() -> AsyncEngine:
    """Get database engine."""
    global engine
    if engine is None:
        engine = create_engine()
    return engine


# Create session factory (will be initialized later)
SessionLocal = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    global SessionLocal
    
    if SessionLocal is None:
        from sqlalchemy.ext.asyncio import async_sessionmaker
        SessionLocal = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


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
                "url": settings.DATABASE_URL.split("@")[1] if "@" in (settings.DATABASE_URL or "") else "hidden"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "url": settings.DATABASE_URL.split("@")[1] if "@" in (settings.DATABASE_URL or "") else "hidden"
        }