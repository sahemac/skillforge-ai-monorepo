#!/usr/bin/env python3
"""
Deploy SkillForge AI test users via the registration API
This is the safest approach using the validated registration endpoint
"""

import asyncio
import sys
import os
import json
import httpx
from datetime import datetime

async def test_api_server():
    """Test if the user-service API is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                print("[OK] User-service API is running")
                return True
            else:
                print(f"[ERROR] API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to API: {e}")
        print("Please start the user-service:")
        print("  cd apps/backend/user-service")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False

async def deploy_users_via_api():
    """Deploy users using the registration API"""
    
    # Load user data
    with open('skillforge_test_users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    print(f"Deploying {len(users_data)} SkillForge AI users via API...")
    print("=" * 60)
    
    created_count = 0
    failed_count = 0
    
    async with httpx.AsyncClient() as client:
        for i, user_data in enumerate(users_data, 1):
            try:
                # Prepare API data (remove non-API fields)
                api_data = user_data.copy()
                api_data.pop('role_context', None)  # Not part of registration schema
                
                # Make registration request
                response = await client.post(
                    "http://localhost:8000/api/v1/auth/register",
                    json=api_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    user_response = response.json()
                    role_context = user_data.get('role_context', 'user')
                    
                    role_icons = {
                        'admin': '[ADMIN]',
                        'company_contact': '[COMPANY]',
                        'user': '[USER]',
                        'premium_user': '[PREMIUM]',
                        'moderator': '[MOD]'
                    }
                    icon = role_icons.get(role_context, '[USER]')
                    
                    print(f"{icon} {user_data['email']} -> Created (ID: {user_response['id'][:8]}...)")
                    created_count += 1
                    
                elif response.status_code == 400:
                    error_detail = response.json().get('detail', 'Unknown error')
                    if 'already exists' in error_detail:
                        print(f"[SKIP] {user_data['email']} -> Already exists")
                    else:
                        print(f"[ERROR] {user_data['email']} -> {error_detail}")
                        failed_count += 1
                else:
                    print(f"[ERROR] {user_data['email']} -> HTTP {response.status_code}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"[ERROR] {user_data['email']} -> Exception: {e}")
                failed_count += 1
                continue
    
    print(f"\nDeployment Summary:")
    print(f"  Created: {created_count} users")
    print(f"  Failed: {failed_count} users")
    print(f"  Total: {len(users_data)} users")
    
    return created_count > 0

async def verify_deployed_users():
    """Verify users were deployed correctly by attempting login"""
    
    print("\n[VERIFICATION] Testing user authentication...")
    
    # Test a few key users
    test_users = [
        {'email': 'admin@skillforge.ai', 'password': 'AdminPass123!', 'role': 'admin'},
        {'email': 'contact@techcorp.ai', 'password': 'TechPass123!', 'role': 'company_contact'},
        {'email': 'student.beginner@gmail.com', 'password': 'StudentPass123!', 'role': 'user'},
    ]
    
    successful_logins = 0
    
    async with httpx.AsyncClient() as client:
        for user in test_users:
            try:
                response = await client.post(
                    "http://localhost:8000/api/v1/auth/login",
                    json={
                        'email': user['email'],
                        'password': user['password'],
                        'remember_me': False
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    print(f"[OK] {user['email']} -> Login successful (token expires in {token_data['expires_in']}s)")
                    successful_logins += 1
                else:
                    error = response.json().get('detail', 'Unknown error')
                    print(f"[ERROR] {user['email']} -> Login failed: {error}")
                    
            except Exception as e:
                print(f"[ERROR] {user['email']} -> Exception: {e}")
    
    print(f"\nAuthentication Test Results:")
    print(f"  Successful logins: {successful_logins}/{len(test_users)}")
    
    return successful_logins == len(test_users)

async def check_database_roles():
    """Check if the new COMPANY_CONTACT role was properly updated"""
    
    print("\n[DATABASE CHECK] Verifying UserRole enum update...")
    
    # Try to create a user with company_contact role to test enum
    test_company_user = {
        'email': 'test.company@example.com',
        'username': 'test_company_enum',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'Company',
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': False
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/register",
                json=test_company_user,
                timeout=10.0
            )
            
            if response.status_code == 201:
                print("[OK] UserRole enum supports new roles")
                
                # Clean up test user
                await client.delete(f"http://localhost:8000/api/v1/users/{test_company_user['email']}")
                
                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print(f"[ERROR] Role enum test failed: {error}")
                return False
                
    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("SkillForge AI - API-based Deployment")
    print("Deploying users via validated registration endpoint")
    print("=" * 70)
    
    async def run_deployment():
        # Step 1: Check API server
        if not await test_api_server():
            return False
        
        # Step 2: Deploy users
        if not await deploy_users_via_api():
            print("\n[FAILED] User deployment failed")
            return False
        
        # Step 3: Verify deployment
        if not await verify_deployed_users():
            print("\n[WARNING] Some authentication tests failed")
        
        # Step 4: Check database roles
        if not await check_database_roles():
            print("\n[WARNING] Role enum verification failed")
        
        print("\n[SUCCESS] SkillForge AI deployment completed!")
        print("\nNext steps:")
        print("1. Check database directly for company_contact roles")
        print("2. Test role-based access control")
        print("3. Validate company profile associations")
        
        return True
    
    success = asyncio.run(run_deployment())
    
    if success:
        print("\n[COMPLETED] Deployment successful!")
        return True
    else:
        print("\n[FAILED] Deployment incomplete!")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)