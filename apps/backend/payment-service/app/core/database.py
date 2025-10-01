"""
Database configuration for SkillForge AI Payment Service
SQLModel with async PostgreSQL support
"""

import logging
from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Database URL construction
if settings.DATABASE_URL:
    database_url = settings.DATABASE_URL
else:
    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

# Create async engine with optimized settings for payments
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    poolclass=NullPool if settings.is_development else None,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "server_settings": {
            "jit": "off",  # Disable JIT for faster simple queries
        },
        "command_timeout": 60,
    }
)

# Create session factory
AsyncSessionFactory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_and_tables():
    """Create database tables."""
    try:
        # Import all models to ensure they're registered
        from app.models.payment import Payment, PaymentRefund
        from app.models.subscription import (
            Subscription, SubscriptionPlan, UsageRecord
        )
        from app.models.invoice import (
            Invoice, InvoiceLineItem, WebhookEvent
        )

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


async def drop_db_and_tables():
    """Drop all database tables (use with caution!)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            logger.warning("All database tables dropped")

    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise


async def get_db_health() -> dict:
    """Check database health."""
    try:
        async with AsyncSessionFactory() as session:
            result = await session.exec("SELECT 1")
            result.fetchone()
            return {
                "status": "healthy",
                "database": settings.POSTGRES_DB,
                "host": settings.POSTGRES_HOST,
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_HOST,
        }