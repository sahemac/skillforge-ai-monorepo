#!/usr/bin/env python3
"""
Recreate database with proper User and Company models
Using the definitive models, not the simplified ones
"""

import asyncio
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def recreate_database():
    """Recreate database with correct schema from definitive models."""
    
    print("=" * 70)
    print("SkillForge AI - Database Recreation with Definitive Models")
    print("=" * 70)
    
    try:
        # Stop any existing connections first
        print("\n[1/4] Preparing database recreation...")
        
        # Remove old database file if it exists
        db_files = ['skillforge_dev.db', 'test_auth.db', 'skillforge_complete.db']
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    print(f"  [OK] Removed old database: {db_file}")
                except Exception as e:
                    print(f"  [WARNING] Could not remove {db_file}: {e}")
        
        print("\n[2/4] Importing definitive models...")
        from app.models import (
            User, UserRole, UserStatus, UserSkillLevel,
            UserSession, UserSettings,
            CompanyProfile, CompanySize, IndustryType,
            TeamMember, Subscription
        )
        print("  [OK] Models imported successfully")
        
        print("\n[3/4] Creating database with proper schema...")
        from app.core.database import create_db_and_tables
        await create_db_and_tables()
        print("  [OK] Database and tables created")
        
        print("\n[4/4] Creating test users with proper roles...")
        from app.core.database import get_session
        from app.crud import user as user_crud
        from app.schemas.user import UserCreate
        
        test_users = [
            {
                "email": "admin@skillforge.ai",
                "username": "admin_platform",
                "password": "AdminPass123!",
                "first_name": "Admin",
                "last_name": "Platform",
                "role": UserRole.ADMIN,
                "description": "Platform Administrator"
            },
            {
                "email": "contact@techcorp.ai",
                "username": "techcorp_contact",
                "password": "TechPass123!",
                "first_name": "Tech",
                "last_name": "Corp",
                "role": UserRole.COMPANY_CONTACT,
                "description": "Company Contact"
            },
            {
                "email": "student@skillforge.ai",
                "username": "student_user",
                "password": "StudentPass123!",
                "first_name": "Student",
                "last_name": "User",
                "role": UserRole.USER,
                "description": "Regular Student"
            },
            {
                "email": "premium@skillforge.ai",
                "username": "premium_user",
                "password": "PremiumPass123!",
                "first_name": "Premium",
                "last_name": "User",
                "role": UserRole.PREMIUM_USER,
                "description": "Premium User"
            }
        ]
        
        async for session in get_session():
            created_count = 0
            for user_data in test_users:
                try:
                    # Create UserCreate object with role
                    user_create = UserCreate(
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"],
                        confirm_password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        terms_accepted=True,
                        privacy_policy_accepted=True,
                        role=user_data["role"]  # Specify role
                    )
                    
                    # Create user
                    new_user = await user_crud.create(session, user_create)
                    print(f"  [OK] Created {user_data['description']}: {new_user.email} (Role: {new_user.role.value})")
                    created_count += 1
                    
                except Exception as e:
                    print(f"  [ERROR] Failed to create {user_data['email']}: {e}")
            
            print(f"\n  Created {created_count}/{len(test_users)} users successfully")
            break
        
        print("\n" + "=" * 70)
        print("DATABASE RECREATION COMPLETE")
        print("=" * 70)
        print("\nDatabase: skillforge_dev.db")
        print("Models: Using definitive models (user.py, company.py)")
        print("\nTest users created:")
        print("  - admin@skillforge.ai / AdminPass123! (ADMIN)")
        print("  - contact@techcorp.ai / TechPass123! (COMPANY_CONTACT)")
        print("  - student@skillforge.ai / StudentPass123! (USER)")
        print("  - premium@skillforge.ai / PremiumPass123! (PREMIUM_USER)")
        print("\nNext steps:")
        print("  1. Restart the API: uvicorn app.main:app --reload")
        print("  2. Test authentication with the new users")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database recreation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(recreate_database())
    sys.exit(0 if success else 1)