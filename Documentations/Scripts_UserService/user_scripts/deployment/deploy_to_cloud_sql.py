#!/usr/bin/env python3
"""
Deploy SkillForge AI test users to Cloud SQL PostgreSQL
Updates the database with correct business model users and companies
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from uuid import uuid4
import asyncpg

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user_simple import UserRole, UserStatus, UserSkillLevel
from app.models.company_simple import CompanySize, IndustryType
from app.core.security import get_password_hash

# Cloud SQL connection parameters
DB_CONFIG = {
    'host': 'localhost',  # via Cloud SQL Proxy
    'port': 5432,
    'database': 'skillforge_db',
    'user': 'skillforge_user',
    'password': 'Psaumes@27'
}

async def test_cloud_sql_connection():
    """Test Cloud SQL connection"""
    print("Testing Cloud SQL PostgreSQL connection...")
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    print("")
    
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Test query
        version = await conn.fetchval('SELECT version();')
        print("[OK] Connection successful!")
        print(f"PostgreSQL version: {version[:80]}...")
        
        # Check existing tables
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        print(f"\nExisting tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Is Cloud SQL Proxy running?")
        print("2. Check proxy output for errors")
        print("3. Verify credentials are correct")
        return False

async def update_user_roles_enum():
    """Update UserRole enum in database to include COMPANY_CONTACT"""
    print("\nUpdating UserRole enum in database...")
    
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Check if the enum value already exists
        existing_roles = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid FROM pg_type WHERE typname = 'userrole'
            );
        """)
        
        existing_role_values = [row['enumlabel'] for row in existing_roles]
        print(f"Current enum values: {existing_role_values}")
        
        # Add COMPANY_CONTACT if it doesn't exist
        if 'company_contact' not in existing_role_values:
            await conn.execute("""
                ALTER TYPE userrole ADD VALUE 'company_contact';
            """)
            print("[OK] Added 'company_contact' to UserRole enum")
        else:
            print("[OK] 'company_contact' already exists in UserRole enum")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update enum: {e}")
        return False

async def deploy_skillforge_users():
    """Deploy SkillForge AI users to Cloud SQL"""
    
    # Load user data
    with open('skillforge_test_users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    # Load company data
    with open('skillforge_test_companies.json', 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    print(f"\nDeploying {len(users_data)} users and {len(companies_data)} companies to Cloud SQL...")
    print("=" * 70)
    
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Deploy companies first
        print("\n[STEP 1] Deploying company profiles...")
        company_ids = {}
        
        for company in companies_data:
            try:
                # Check if company already exists
                existing_company = await conn.fetchval(
                    "SELECT id FROM company_profiles WHERE name = $1",
                    company['name']
                )
                
                if existing_company:
                    print(f"  Company {company['name']} already exists, skipping...")
                    company_ids[company['contact_email']] = existing_company
                    continue
                
                # Create company profile
                company_id = uuid4()
                now = datetime.utcnow()
                slug = company['name'].lower().replace(' ', '-').replace('.', '')
                
                await conn.execute("""
                    INSERT INTO company_profiles (
                        id, name, slug, description, industry, size, 
                        contact_email, is_active, is_verified, plan_type,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                    company_id, company['name'], slug, company['description'],
                    company['industry'], company['size'], company['contact_email'],
                    True, False, 'free', now, now
                )
                
                company_ids[company['contact_email']] = company_id
                print(f"  [OK] Created: {company['name']} ({company['industry']})")
                
            except Exception as e:
                print(f"  [ERROR] Failed to create {company['name']}: {e}")
                continue
        
        # Deploy users
        print(f"\n[STEP 2] Deploying users...")
        created_count = 0
        
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = await conn.fetchval(
                    "SELECT id FROM users WHERE email = $1 OR username = $2",
                    user_data['email'], user_data['username']
                )
                
                if existing_user:
                    print(f"  User {user_data['email']} already exists, skipping...")
                    continue
                
                # Hash password
                hashed_password = get_password_hash(user_data['password'])
                
                # Generate UUID and timestamps
                user_id = uuid4()
                now = datetime.utcnow()
                
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
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
                        $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28
                    )
                """, 
                    user_id, user_data['email'], user_data['username'], hashed_password,
                    user_data['first_name'], user_data['last_name'],
                    f"{user_data['first_name']} {user_data['last_name']}",
                    user_data['bio'], user_data['job_title'], user_data['location'],
                    user_data['timezone'], user_data['experience_level'],
                    user_data['skills'], user_data['interests'], user_data['role_context'],
                    UserStatus.ACTIVE.value, True, True, 
                    user_data['role_context'] == 'admin',  # is_superuser
                    False,  # is_premium
                    True,   # newsletter_subscribed
                    now,    # email_verified_at
                    0,      # failed_login_attempts
                    now,    # terms_accepted_at
                    now,    # privacy_policy_accepted_at
                    now,    # created_at
                    now,    # updated_at
                    {}      # metadata
                )
                
                # If user is company contact, create team member association
                if user_data['role_context'] == 'company_contact' and user_data['email'] in company_ids:
                    company_id = company_ids[user_data['email']]
                    team_member_id = uuid4()
                    
                    await conn.execute("""
                        INSERT INTO team_members (
                            id, user_id, company_id, role, title, 
                            is_admin, is_active, joined_at, created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                        team_member_id, user_id, company_id, 'admin',
                        user_data['job_title'], True, True, now, now
                    )
                    
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
                print(f"  [ERROR] Failed to create {user_data['email']}: {e}")
                continue
        
        print(f"\n[STEP 3] Deployment summary:")
        print(f"  Companies deployed: {len([c for c in companies_data])}")
        print(f"  Users created: {created_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Deployment failed: {e}")
        return False

async def verify_deployment():
    """Verify the deployment was successful"""
    print("\n[VERIFICATION] Checking deployed data...")
    
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Check users by role
        users_by_role = await conn.fetch("""
            SELECT role, COUNT(*) as count
            FROM users 
            WHERE email LIKE '%skillforge.ai' OR email LIKE '%@techcorp.ai' 
               OR email LIKE '%@financeplus.com' OR email LIKE '%@healthtech.fr'
               OR email LIKE '%@gmail.com' OR email LIKE '%@outlook.com'
               OR email LIKE '%@yahoo.com' OR email LIKE '%@protonmail.com'
               OR email LIKE '%@icloud.com'
            GROUP BY role
            ORDER BY role;
        """)
        
        print("\nUsers by role:")
        for row in users_by_role:
            print(f"  {row['role']}: {row['count']} users")
        
        # Check companies
        companies = await conn.fetch("""
            SELECT name, industry, size, contact_email, is_verified
            FROM company_profiles
            ORDER BY name;
        """)
        
        print(f"\nCompanies ({len(companies)}):")
        for company in companies:
            verified = "[VERIFIED]" if company['is_verified'] else "[PENDING]"
            print(f"  {verified} {company['name']} ({company['industry']}) - {company['contact_email']}")
        
        # Check team members
        team_members = await conn.fetch("""
            SELECT u.email, u.role as user_role, cp.name as company_name, tm.role as team_role
            FROM team_members tm
            JOIN users u ON tm.user_id = u.id
            JOIN company_profiles cp ON tm.company_id = cp.id
            ORDER BY cp.name;
        """)
        
        print(f"\nTeam members ({len(team_members)}):")
        for member in team_members:
            print(f"  {member['email']} -> {member['company_name']} ({member['team_role']})")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False

async def main():
    """Main deployment function"""
    print("SkillForge AI - Cloud SQL PostgreSQL Deployment")
    print("Deploying correct business model users and companies")
    print("=" * 80)
    
    # Step 1: Test connection
    if not await test_cloud_sql_connection():
        print("\n[FAILED] Cannot connect to Cloud SQL")
        print("Please ensure Cloud SQL Proxy is running:")
        print("./cloud_sql_proxy skillforge-ai-mvp-25:europe-west1:skillforge-db")
        return False
    
    # Step 2: Update enum if needed
    if not await update_user_roles_enum():
        print("\n[FAILED] Could not update UserRole enum")
        return False
    
    # Step 3: Deploy users and companies
    if not await deploy_skillforge_users():
        print("\n[FAILED] Deployment failed")
        return False
    
    # Step 4: Verify deployment
    if not await verify_deployment():
        print("\n[FAILED] Verification failed")
        return False
    
    print("\n[SUCCESS] SkillForge AI deployment to Cloud SQL completed!")
    print("\nNext steps:")
    print("1. Validate company accounts via admin interface")
    print("2. Test user authentication with deployed accounts")
    print("3. Verify role-based access control")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n[COMPLETED] All operations successful!")
        sys.exit(0)
    else:
        print("\n[FAILED] Deployment incomplete!")
        sys.exit(1)