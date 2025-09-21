#!/usr/bin/env python3
"""
Déploiement complet SkillForge AI avec SQLite
Crée la base, les tables, et insère tous les utilisateurs de test
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from uuid import uuid4

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from app.models.base import SQLModel
from app.models.user_simple import UserRole, UserStatus, UserSkillLevel
from app.core.security import get_password_hash

# SQLite database
DATABASE_URL = "sqlite+aiosqlite:///./skillforge_complete.db"

async def deploy_complete_skillforge():
    """Déploiement complet SkillForge AI avec SQLite"""
    
    print("SkillForge AI - Complete SQLite Deployment")
    print("Creating database, tables, companies, and users")
    print("=" * 70)
    
    # Load test data
    with open('skillforge_test_users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    with open('skillforge_test_companies.json', 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    print(f"Preparing to deploy:")
    print(f"  - Database: SQLite (skillforge_complete.db)")
    print(f"  - Users: {len(users_data)}")
    print(f"  - Companies: {len(companies_data)}")
    
    try:
        # Create engine with optimized settings
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            },
        )
        
        print("\n[STEP 1] Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("[OK] All tables created successfully")
        
        print("\n[STEP 2] Inserting companies...")
        async with engine.begin() as conn:
            company_ids = {}
            
            for company in companies_data:
                try:
                    company_id = str(uuid4())
                    now = datetime.utcnow().isoformat()
                    slug = company['name'].lower().replace(' ', '-').replace('.', '')
                    
                    # Insert company
                    await conn.execute("""
                        INSERT INTO company_profiles (
                            id, name, slug, description, industry, size,
                            contact_email, is_active, is_verified, plan_type,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        company_id, company['name'], slug, company['description'],
                        company['industry'], company['size'], company['contact_email'],
                        1, 0, 'free', now, now  # SQLite uses integers for booleans
                    ))
                    
                    company_ids[company['contact_email']] = company_id
                    print(f"  [OK] {company['name']} ({company['industry']})")
                    
                except Exception as e:
                    print(f"  [ERROR] {company['name']}: {e}")
                    continue
        
        print(f"\n[STEP 3] Inserting users...")
        async with engine.begin() as conn:
            created_count = 0
            
            for user_data in users_data:
                try:
                    # Hash password
                    hashed_password = get_password_hash(user_data['password'])
                    
                    # Generate UUID and timestamps
                    user_id = str(uuid4())
                    now = datetime.utcnow().isoformat()
                    
                    # Insert user
                    await conn.execute("""
                        INSERT INTO users (
                            id, email, username, hashed_password, first_name, last_name,
                            full_name, bio, job_title, location, timezone,
                            experience_level, skills, interests, role, status,
                            is_active, is_verified, is_superuser, is_premium,
                            newsletter_subscribed, email_verified_at, failed_login_attempts,
                            terms_accepted_at, privacy_policy_accepted_at, created_at,
                            updated_at, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, user_data['email'], user_data['username'], hashed_password,
                        user_data['first_name'], user_data['last_name'],
                        f"{user_data['first_name']} {user_data['last_name']}",
                        user_data['bio'], user_data['job_title'], user_data['location'],
                        user_data['timezone'], user_data['experience_level'],
                        json.dumps(user_data['skills']), json.dumps(user_data['interests']),
                        user_data['role_context'], UserStatus.ACTIVE.value,
                        1, 1, 1 if user_data['role_context'] == 'admin' else 0,  # SQLite integers
                        0, 1, now, 0, now, now, now, now, "{}"
                    ))
                    
                    # Create team member if company contact
                    if user_data['role_context'] == 'company_contact' and user_data['email'] in company_ids:
                        company_id = company_ids[user_data['email']]
                        team_member_id = str(uuid4())
                        
                        await conn.execute("""
                            INSERT INTO team_members (
                                id, user_id, company_id, role, title,
                                is_admin, is_active, joined_at, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            team_member_id, user_id, company_id, 'admin',
                            user_data['job_title'], 1, 1, now, now
                        ))
                        
                        print(f"  [COMPANY] {user_data['email']} -> {user_data['role_context']}")
                    else:
                        role_icons = {
                            'admin': '[ADMIN]',
                            'user': '[USER]',
                            'premium_user': '[PREMIUM]',
                            'moderator': '[MOD]'
                        }
                        icon = role_icons.get(user_data['role_context'], '[USER]')
                        print(f"  {icon} {user_data['email']} -> {user_data['role_context']}")
                    
                    created_count += 1
                    
                except Exception as e:
                    print(f"  [ERROR] {user_data['email']}: {e}")
                    continue
        
        print(f"\n[STEP 4] Verification...")
        async with engine.begin() as conn:
            
            # Count users by role
            result = await conn.execute("""
                SELECT role, COUNT(*) as count
                FROM users
                GROUP BY role
                ORDER BY role
            """)
            users_by_role = result.fetchall()
            
            print("\nUsers by role:")
            total_users = 0
            for row in users_by_role:
                print(f"  {row[0]}: {row[1]} users")
                total_users += row[1]
            
            # Count companies
            result = await conn.execute("SELECT COUNT(*) FROM company_profiles")
            company_count = result.fetchone()[0]
            
            # Count team members
            result = await conn.execute("SELECT COUNT(*) FROM team_members")
            team_member_count = result.fetchone()[0]
            
            print(f"\nDeployment statistics:")
            print(f"  Total users: {total_users}")
            print(f"  Companies: {company_count}")
            print(f"  Team members: {team_member_count}")
        
        await engine.dispose()
        
        print(f"\n[SUCCESS] SkillForge AI deployment completed!")
        print(f"Database file: {DATABASE_URL}")
        print(f"Users created: {created_count}")
        print(f"Companies created: {len(companies_data)}")
        
        # Create connection info for API
        connection_info = {
            'database_url': DATABASE_URL,
            'database_type': 'sqlite',
            'users_count': created_count,
            'companies_count': len(companies_data),
            'deployment_time': datetime.utcnow().isoformat()
        }
        
        with open('deployment_info.json', 'w') as f:
            json.dump(connection_info, f, indent=2)
        
        print(f"\nNext steps:")
        print(f"1. Update app configuration to use SQLite")
        print(f"2. Start user-service API: uvicorn app.main:app --reload")
        print(f"3. Test authentication with deployed users")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = asyncio.run(deploy_complete_skillforge())
    
    if success:
        print("\n[COMPLETED] SkillForge AI deployment successful!")
        print("Ready to start user-service API and test authentication!")
        return True
    else:
        print("\n[FAILED] SkillForge AI deployment failed!")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)