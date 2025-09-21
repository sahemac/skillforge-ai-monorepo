#!/usr/bin/env python3
"""
Setup local test database for SkillForge AI User Service
"""

import os
import sys
import asyncio

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from app.models.base import SQLModel

# Import all models to ensure they are registered
from app.models.user_simple import User, UserSettings, UserSession  
from app.models.company_simple import CompanyProfile, TeamMember, Subscription

async def setup_test_database():
    """Setup test database with all tables"""
    
    # Database URL for testing
    TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_skillforge.db"
    
    print("🗄️  Setting up test database...")
    print(f"📁 Database: {TEST_DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("✅ Test database created successfully!")
        
        # Test the connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            test_result = result.fetchone()
            print(f"🔍 Connection test: {test_result}")
        
        await engine.dispose()
        
        # List all tables created
        print("\n📊 Tables created:")
        for table_name in SQLModel.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return False

def main():
    """Main function"""
    print("🚀 SkillForge AI User Service - Test Database Setup")
    
    # Change to service directory
    service_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(service_dir)
    print(f"📁 Working directory: {service_dir}")
    
    # Setup database
    success = asyncio.run(setup_test_database())
    
    if success:
        print("\n🎉 Test database setup completed!")
        print("Ready to run tests with:")
        print("  pytest app/tests/ -v")
        return True
    else:
        print("\n💥 Test database setup failed!")
        return False

if __name__ == "__main__":
    if main():
        print("\n✅ All done!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)