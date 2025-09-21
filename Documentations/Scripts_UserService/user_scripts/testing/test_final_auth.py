#!/usr/bin/env python3
"""
Test final authentication with definitive models
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_final_authentication():
    """Test authentication with definitive models using fresh database."""
    
    print("=" * 70)
    print("SkillForge AI - Final Authentication Test")
    print("=" * 70)
    
    try:
        # Use a fresh database name
        db_name = f"skillforge_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///./{db_name}"
        
        print(f"\n[1/5] Using fresh database: {db_name}")
        
        print("\n[2/5] Importing definitive models...")
        from app.models import (
            User, UserRole, UserStatus, UserSkillLevel,
            UserSession, UserSettings,
            CompanyProfile, CompanySize, IndustryType,
            TeamMember, Subscription
        )
        print("  [OK] Definitive models imported successfully")
        
        print("\n[3/5] Creating database with proper schema...")
        from app.core.database import create_db_and_tables
        await create_db_and_tables()
        print("  [OK] Database and tables created")
        
        print("\n[4/5] Creating test users...")
        from app.core.database import get_session
        from app.crud import user as user_crud
        from app.schemas.user import UserCreate
        
        test_users = [
            {
                "email": "admin@skillforge.ai",
                "username": "admin_test",
                "password": "AdminPass123!",
                "first_name": "Admin",
                "last_name": "Test",
                "role": UserRole.ADMIN,
                "description": "Platform Administrator"
            },
            {
                "email": "company@techcorp.ai",
                "username": "company_contact",
                "password": "CompanyPass123!",
                "first_name": "Company",
                "last_name": "Contact",
                "role": UserRole.COMPANY_CONTACT,
                "description": "Company Contact"
            },
            {
                "email": "student@skillforge.ai",
                "username": "student_test",
                "password": "StudentPass123!",
                "first_name": "Student",
                "last_name": "Test",
                "role": UserRole.USER,
                "description": "Regular Student"
            }
        ]
        
        created_users = []
        async for session in get_session():
            for user_data in test_users:
                try:
                    # Create UserCreate object
                    user_create = UserCreate(
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"],
                        confirm_password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        terms_accepted=True,
                        privacy_policy_accepted=True,
                        role=user_data["role"]
                    )
                    
                    # Create user
                    new_user = await user_crud.create(session, user_create)
                    created_users.append({
                        "user": new_user,
                        "password": user_data["password"],
                        "description": user_data["description"]
                    })
                    print(f"  [OK] Created {user_data['description']}: {new_user.email} (Role: {new_user.role.value})")
                    
                except Exception as e:
                    print(f"  [ERROR] Failed to create {user_data['email']}: {e}")
            
            break
        
        print(f"\n[5/5] Testing authentication...")
        
        # Test authentication for each user
        for user_info in created_users:
            user = user_info["user"]
            password = user_info["password"]
            description = user_info["description"]
            
            try:
                async for session in get_session():
                    # Test authentication
                    authenticated_user = await user_crud.authenticate(
                        session, 
                        email=user.email, 
                        password=password
                    )
                    
                    if authenticated_user:
                        print(f"  [OK] Authentication successful for {description}: {user.email}")
                        
                        # Test user details access
                        assert authenticated_user.email == user.email
                        assert authenticated_user.role == user.role
                        assert authenticated_user.is_active is True
                        
                        print(f"       - Role: {authenticated_user.role.value}")
                        print(f"       - Status: {authenticated_user.status.value}")
                        print(f"       - Verified: {authenticated_user.is_verified}")
                        
                    else:
                        print(f"  [ERROR] Authentication failed for {description}: {user.email}")
                    
                    break
                    
            except Exception as e:
                print(f"  [ERROR] Authentication test failed for {description}: {e}")
        
        print("\n" + "=" * 70)
        print("FINAL AUTHENTICATION TEST COMPLETE")
        print("=" * 70)
        print(f"\nTest Database: {db_name}")
        print("Models: Using definitive models (user.py, company.py)")
        print("\nAll authentication tests completed!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Final authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_final_authentication())
    sys.exit(0 if success else 1)