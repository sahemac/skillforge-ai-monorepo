#!/usr/bin/env python3
"""
Script to apply database migrations to PostgreSQL Cloud SQL
Bypasses Alembic environment configuration issues
"""
import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import command
from alembic.config import Config

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.user import User, UserSettings, UserSession
from app.models.base import SQLModel

async def run_migrations():
    """Apply migrations to PostgreSQL database via Cloud SQL Proxy"""
    
    # Database connection via Cloud SQL Proxy (port 5432)
    DATABASE_URL = "postgresql+asyncpg://skillforge_user:Psaumes%4027@127.0.0.1:5432/skillforge_db"
    
    print(f"Connecting to: {DATABASE_URL}")
    
    # Create engine 
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        # Test connection
        async with engine.begin() as conn:
            print("✅ Database connection successful")
            
            # Create all tables using SQLModel
            await conn.run_sync(SQLModel.metadata.create_all)
            print("✅ All tables created/updated")
            
        # Now run Alembic migrations
        os.environ["DATABASE_URL"] = DATABASE_URL
        os.environ["POSTGRES_PASSWORD"] = "Psaumes@27"
        os.environ["POSTGRES_HOST"] = "127.0.0.1"
        os.environ["POSTGRES_PORT"] = "5432"
        
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL.replace("+asyncpg", ""))
        
        # Apply migrations
        print("Applying Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations applied successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migrations())