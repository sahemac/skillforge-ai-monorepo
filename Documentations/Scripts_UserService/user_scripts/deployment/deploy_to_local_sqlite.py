#!/usr/bin/env python3
"""
Deploy SkillForge AI test users to local SQLite (for testing)
Tests the deployment logic before pushing to Cloud SQL
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

# SQLite database for local testing
DATABASE_URL = "sqlite+aiosqlite:///./skillforge_local_test.db"

async def deploy_to_local_sqlite():
    """Deploy SkillForge AI data to local SQLite for testing"""
    
    print("SkillForge AI - Local SQLite Deployment (Testing)")
    print("=" * 60)
    
    # Load test data
    with open('skillforge_test_users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    with open('skillforge_test_companies.json', 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    print(f"Deploying {len(users_data)} users and {len(companies_data)} companies...")
    
    try:
        # Create engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("[OK] Database tables created")
        
        # Insert data using raw SQL (SQLite compatible)
        async with engine.begin() as conn:
            
            # Insert companies first
            print("\n[STEP 1] Inserting companies...")
            company_ids = {}
            
            for company in companies_data:
                try:
                    company_id = str(uuid4())
                    now = datetime.utcnow().isoformat()
                    slug = company['name'].lower().replace(' ', '-').replace('.', '')
                    
                    await conn.execute("""
                        INSERT INTO company_profiles (
                            id, name, slug, description, industry, size,
                            contact_email, is_active, is_verified, plan_type,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        company_id, company['name'], slug, company['description'],
                        company['industry'], company['size'], company['contact_email'],
                        True, False, 'free', now, now
                    ))
                    
                    company_ids[company['contact_email']] = company_id
                    print(f"  [OK] {company['name']} ({company['industry']})")
                    
                except Exception as e:
                    print(f"  [ERROR] {company['name']}: {e}")
                    continue
            
            # Insert users
            print(f"\n[STEP 2] Inserting users...")
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
                        True, True, user_data['role_context'] == 'admin',
                        False, True, now, 0, now, now, now, now, "{}"
                    ))
                    
                    # If user is company contact, create team member association
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
                            user_data['job_title'], True, True, now, now
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
        
        # Verify deployment
        print(f"\n[STEP 3] Verification...")
        async with engine.begin() as conn:
            
            # Check users by role
            result = await conn.execute("""
                SELECT role, COUNT(*) as count
                FROM users
                GROUP BY role
                ORDER BY role
            """)
            users_by_role = result.fetchall()
            
            print("Users by role:")
            for row in users_by_role:
                print(f"  {row[0]}: {row[1]} users")
            
            # Check companies
            result = await conn.execute("""
                SELECT name, industry, contact_email
                FROM company_profiles
                ORDER BY name
            """)
            companies = result.fetchall()
            
            print(f"\nCompanies ({len(companies)}):")
            for company in companies:
                print(f"  {company[0]} ({company[1]}) - {company[2]}")
            
            # Check team members
            result = await conn.execute("""
                SELECT u.email, cp.name
                FROM team_members tm
                JOIN users u ON tm.user_id = u.id
                JOIN company_profiles cp ON tm.company_id = cp.id
                ORDER BY cp.name
            """)
            team_members = result.fetchall()
            
            print(f"\nTeam members ({len(team_members)}):")
            for member in team_members:
                print(f"  {member[0]} -> {member[1]}")
        
        await engine.dispose()
        
        print(f"\n[SUCCESS] Local SQLite deployment completed!")
        print(f"  Database: {DATABASE_URL}")
        print(f"  Users created: {created_count}")
        print(f"  Companies created: {len(companies_data)}")
        print("\nReady for Cloud SQL deployment!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Local deployment failed: {e}")
        return False

def main():
    """Main function"""
    success = asyncio.run(deploy_to_local_sqlite())
    
    if success:
        print("\n[COMPLETED] Local testing successful!")
        return True
    else:
        print("\n[FAILED] Local testing failed!")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)