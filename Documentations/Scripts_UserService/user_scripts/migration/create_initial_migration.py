#!/usr/bin/env python3
"""
Create initial Alembic migration for SkillForge AI User Service
"""

import os
import sys
import subprocess

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_initial_migration():
    """Create initial migration with all models"""
    
    # Ensure we're in the right directory
    service_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(service_dir)
    
    print("🏗️  Creating initial migration...")
    
    try:
        # Create initial migration
        result = subprocess.run([
            'alembic', 'revision', '--autogenerate', 
            '-m', 'Initial migration with User, UserSettings, UserSession, CompanyProfile, TeamMember, Subscription'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Initial migration created successfully!")
        print(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating migration: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False

if __name__ == "__main__":
    print("🧪 Creating initial migration for SkillForge AI User Service...")
    
    if create_initial_migration():
        print("\n🎉 Initial migration created!")
        print("Next steps:")
        print("1. Review the generated migration file in alembic/versions/")
        print("2. Apply the migration: alembic upgrade head")
        print("3. Run tests to verify everything works")
    else:
        print("\n💥 Failed to create initial migration!")
        sys.exit(1)