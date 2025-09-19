#!/usr/bin/env python3
"""
Run migration for SkillForge AI User Service using cloud database
"""

import os
import sys
import subprocess

# Database URL for cloud PostgreSQL via Cloud SQL Proxy
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/dbname")

def test_connection():
    """Test database connection before migration"""
    print("🔍 Testing database connection...")
    
    try:
        import asyncio
        import asyncpg
        from urllib.parse import urlparse
        
        async def connect():
            parsed = urlparse(DATABASE_URL)
            conn = await asyncpg.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading /
                user=parsed.username,
                password=parsed.password
            )
            result = await conn.fetchval('SELECT version();')
            print(f"✅ Connected to: {result[:50]}...")
            await conn.close()
            return True
        
        return asyncio.run(connect())
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_migration():
    """Create initial migration"""
    print("🏗️  Creating migration...")
    
    try:
        env = os.environ.copy()
        env['DATABASE_URL'] = DATABASE_URL
        
        result = subprocess.run([
            'alembic', 'revision', '--autogenerate',
            '-m', 'Initial migration with all models'
        ], env=env, capture_output=True, text=True, check=True)
        
        print("✅ Migration created successfully!")
        print(f"Output: {result.stdout}")
        return True
        
    except Exception as e:
        print(f"❌ Migration creation failed: {e}")
        return False

def apply_migration():
    """Apply migration to database"""
    print("📊 Applying migration to database...")
    
    try:
        env = os.environ.copy()
        env['DATABASE_URL'] = DATABASE_URL
        
        result = subprocess.run([
            'alembic', 'upgrade', 'head'
        ], env=env, capture_output=True, text=True, check=True)
        
        print("✅ Migration applied successfully!")
        print(f"Output: {result.stdout}")
        return True
        
    except Exception as e:
        print(f"❌ Migration application failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 SkillForge AI User Service - Database Migration")
    print(f"📍 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unknown'}")
    
    # Change to service directory
    service_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(service_dir)
    print(f"📁 Working directory: {service_dir}")
    
    # Step 1: Test connection
    if not test_connection():
        print("💥 Cannot connect to database. Exiting.")
        return False
    
    # Step 2: Create migration (if needed)
    migrations_dir = os.path.join(service_dir, 'alembic', 'versions')
    if not os.listdir(migrations_dir):
        print("📝 No migrations found, creating initial migration...")
        if not create_migration():
            return False
    else:
        print("📝 Migrations already exist, skipping creation...")
    
    # Step 3: Apply migration
    if not apply_migration():
        return False
    
    print("\n🎉 Database migration completed successfully!")
    print("Ready to run tests!")
    return True

if __name__ == "__main__":
    if main():
        print("\n✅ All done!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)