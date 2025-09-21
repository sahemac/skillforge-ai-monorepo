#!/usr/bin/env python3
"""
Check deployment status and provide instructions
Verifies current state and gives next steps
"""

import asyncio
import sys
import os
import json
import asyncpg
import httpx

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def check_cloud_sql_status():
    """Check Cloud SQL Proxy status"""
    print("[CHECK 1] Cloud SQL Proxy Connection")
    print("-" * 40)
    
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='skillforge_db',
            user='skillforge_user',
            password='Psaumes@27',
            timeout=3
        )
        
        # Test connection and get info
        db_name = await conn.fetchval('SELECT current_database();')
        version = await conn.fetchval('SELECT version();')
        
        print(f"[OK] Connected to: {db_name}")
        print(f"[OK] PostgreSQL version: {version[:50]}...")
        
        # Check table existence
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        print(f"[OK] Found {len(tables)} tables:")
        for table in tables:
            print(f"     - {table['tablename']}")
        
        # Check UserRole enum values
        try:
            roles = await conn.fetch("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'userrole'
                );
            """)
            
            role_values = [r['enumlabel'] for r in roles]
            print(f"[OK] UserRole enum values: {role_values}")
            
            if 'company_contact' in role_values:
                print("[OK] COMPANY_CONTACT role is available")
            else:
                print("[WARNING] COMPANY_CONTACT role missing from enum")
                
        except Exception as e:
            print(f"[WARNING] Could not check UserRole enum: {e}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Cloud SQL connection failed: {e}")
        print("\nTo start Cloud SQL Proxy:")
        print("1. Download cloud_sql_proxy if not done")
        print("2. Run: ./cloud_sql_proxy skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging")
        print("3. Wait for 'Ready for new connections' message")
        return False

async def check_api_server_status():
    """Check if user-service API is running"""
    print("\n[CHECK 2] User-Service API Status")
    print("-" * 40)
    
    try:
        async with httpx.AsyncClient() as client:
            # Try health check
            response = await client.get("http://localhost:8000/health", timeout=3.0)
            
            if response.status_code == 200:
                print("[OK] User-service API is running")
                
                # Try to get API info
                try:
                    info_response = await client.get("http://localhost:8000/", timeout=3.0)
                    if info_response.status_code == 200:
                        print("[OK] API endpoints accessible")
                except:
                    print("[WARNING] API info endpoint not accessible")
                
                return True
            else:
                print(f"[ERROR] API returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"[ERROR] Cannot connect to API: {e}")
        print("\nTo start user-service API:")
        print("1. cd apps/backend/user-service")
        print("2. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("3. Wait for 'Application startup complete' message")
        return False

async def check_existing_users():
    """Check what users already exist"""
    print("\n[CHECK 3] Existing Users in Database")
    print("-" * 40)
    
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='skillforge_db',
            user='skillforge_user',
            password='Psaumes@27',
            timeout=3
        )
        
        # Count users by role
        users_by_role = await conn.fetch("""
            SELECT role, COUNT(*) as count
            FROM users 
            GROUP BY role
            ORDER BY role;
        """)
        
        if users_by_role:
            print("Current users by role:")
            for row in users_by_role:
                print(f"  {row['role']}: {row['count']} users")
        else:
            print("[INFO] No users found in database")
        
        # Check for SkillForge test users
        skillforge_users = await conn.fetch("""
            SELECT email, role, is_active
            FROM users 
            WHERE email LIKE '%skillforge.ai' 
               OR email LIKE '%@techcorp.ai'
               OR email LIKE '%@financeplus.com'
               OR email LIKE '%@healthtech.fr'
            ORDER BY email;
        """)
        
        if skillforge_users:
            print(f"\nSkillForge test users ({len(skillforge_users)}):")
            for user in skillforge_users:
                status = "ACTIVE" if user['is_active'] else "INACTIVE"
                print(f"  {user['email']} ({user['role']}) - {status}")
        else:
            print("\n[INFO] No SkillForge test users found")
        
        await conn.close()
        return len(skillforge_users)
        
    except Exception as e:
        print(f"[ERROR] Cannot check users: {e}")
        return None

def check_test_data_files():
    """Check if test data files exist"""
    print("\n[CHECK 4] Test Data Files")
    print("-" * 40)
    
    files_to_check = [
        'skillforge_test_users.json',
        'skillforge_test_companies.json',
        'create_skillforge_test_users.py',
        'deploy_to_cloud_sql.py',
        'deploy_via_api.py'
    ]
    
    all_exist = True
    
    for filename in files_to_check:
        if os.path.exists(filename):
            # Get file size
            size = os.path.getsize(filename)
            print(f"[OK] {filename} ({size} bytes)")
        else:
            print(f"[ERROR] {filename} missing")
            all_exist = False
    
    return all_exist

async def main():
    """Main status check function"""
    print("SkillForge AI - Deployment Status Check")
    print("Verifying current state and next steps")
    print("=" * 70)
    
    # Check all components
    cloud_sql_ok = await check_cloud_sql_status()
    api_ok = await check_api_server_status()
    existing_users = await check_existing_users() if cloud_sql_ok else None
    files_ok = check_test_data_files()
    
    # Summary and recommendations
    print("\n" + "=" * 70)
    print("DEPLOYMENT STATUS SUMMARY")
    print("=" * 70)
    
    print(f"Cloud SQL Proxy:  {'[OK]' if cloud_sql_ok else '[FAILED]'}")
    print(f"User-Service API: {'[OK]' if api_ok else '[FAILED]'}")
    print(f"Test Data Files:  {'[OK]' if files_ok else '[FAILED]'}")
    
    if existing_users is not None:
        print(f"Existing Users:   {existing_users} SkillForge test users found")
    else:
        print("Existing Users:   [CANNOT CHECK]")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS:")
    print("-" * 20)
    
    if not cloud_sql_ok:
        print("1. [PRIORITY] Start Cloud SQL Proxy first")
        print("   Command: ./cloud_sql_proxy skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging")
    
    if not api_ok:
        print("2. Start User-Service API")
        print("   Command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    if cloud_sql_ok and api_ok:
        if existing_users == 0:
            print("3. Deploy SkillForge test users")
            print("   Command: python deploy_via_api.py")
        else:
            print("3. [INFO] SkillForge test users already deployed")
            print("   You can re-run deployment to update/add missing users")
    
    if not files_ok:
        print("4. [ERROR] Some required files are missing")
        print("   Re-run: python create_skillforge_test_users.py")
    
    print(f"\nNext steps:")
    if cloud_sql_ok and api_ok and files_ok:
        print("- System ready for deployment!")
        print("- Run: python deploy_via_api.py")
    else:
        print("- Fix the issues above first")
        print("- Re-run this status check")

if __name__ == "__main__":
    asyncio.run(main())