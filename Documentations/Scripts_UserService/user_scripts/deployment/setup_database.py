#!/usr/bin/env python3
"""
Script to setup PostgreSQL database for SkillForge AI
"""

import asyncio
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.base import SQLModel
from app.models.user_simple import User, UserSettings, UserSession
from app.models.company_simple import CompanyProfile, TeamMember, Subscription

async def setup_database():
    """Setup database and user for SkillForge AI"""
    
    # Try to connect to PostgreSQL as default user
    admin_conn_str = "postgresql://postgres@localhost:5432/postgres"
    
    try:
        print("🔍 Connecting to PostgreSQL...")
        conn = await asyncpg.connect(admin_conn_str)
        
        # Create database if not exists
        try:
            print("🏗️  Creating database 'skillforge_db'...")
            await conn.execute("CREATE DATABASE skillforge_db")
            print("✅ Database 'skillforge_db' created")
        except asyncpg.DuplicateDatabaseError:
            print("ℹ️  Database 'skillforge_db' already exists")
        
        # Create user if not exists
        try:
            print("👤 Creating user 'skillforge_user'...")
            await conn.execute("CREATE USER skillforge_user WITH PASSWORD 'Psaumes@27'")
            print("✅ User 'skillforge_user' created")
        except asyncpg.DuplicateObjectError:
            print("ℹ️  User 'skillforge_user' already exists")
        
        # Grant privileges
        print("🔑 Granting privileges...")
        await conn.execute("GRANT ALL PRIVILEGES ON DATABASE skillforge_db TO skillforge_user")
        await conn.execute("ALTER USER skillforge_user CREATEDB")
        print("✅ Privileges granted")
        
        await conn.close()
        
        # Now connect to skillforge_db and create tables
        print("📊 Creating tables...")
        app_conn_str = "postgresql://skillforge_user:Psaumes%4027@localhost:5432/skillforge_db"
        
        # Use SQLAlchemy sync engine for table creation
        from sqlalchemy import create_engine
        engine = create_engine(app_conn_str.replace('+asyncpg', '').replace('%40', '@'))
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        print("✅ Tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("Database: skillforge_db")
        print("User: skillforge_user") 
        print("Connection string: postgresql://skillforge_user:Psaumes%4027@localhost:5432/skillforge_db")
    else:
        print("\n💥 Database setup failed!")
        sys.exit(1)