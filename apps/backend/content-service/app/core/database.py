"""
Database configuration and utilities for Content Service
"""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create declarative base
Base = declarative_base()

# Database engine
engine = None
AsyncSessionLocal = None


def get_database_url() -> str:
    """Get database URL from settings."""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL

    # Construct URL from individual components
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


async def init_db():
    """Initialize database connection."""
    global engine, AsyncSessionLocal

    try:
        database_url = get_database_url()

        engine = create_async_engine(
            database_url,
            echo=settings.is_development,
            poolclass=NullPool if settings.is_development else None,
            pool_pre_ping=True,
        )

        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)

        logger.info("✓ Database connection established")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    if not AsyncSessionLocal:
        await init_db()

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connection."""
    global engine
    if engine:
        await engine.dispose()
        logger.info("✓ Database connection closed")