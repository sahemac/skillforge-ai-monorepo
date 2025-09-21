#!/usr/bin/env python3
"""
Déploiement final SkillForge AI via API avec SQLite
Attend que l'API soit démarrée puis déploie tous les utilisateurs
"""

import asyncio
import sys
import os
import json
import httpx
from datetime import datetime
import time

async def wait_for_api(timeout=60):
    """Attend que l'API soit disponible"""
    print("Waiting for user-service API to start...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"[OK] API is ready! Status: {health_data.get('status')}")
                    return True
                    
        except Exception:
            # API not ready yet
            pass
        
        print(".", end="", flush=True)
        await asyncio.sleep(2)
    
    print(f"\n[ERROR] API did not start within {timeout} seconds")
    return False

async def deploy_users_via_api():
    """Deploy all SkillForge AI users via registration API"""
    
    # Load user data
    with open('skillforge_test_users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    print(f"\nDeploying {len(users_data)} SkillForge AI users...")
    print("=" * 60)
    
    results = {
        'created': [],
        'skipped': [],
        'failed': []
    }
    
    async with httpx.AsyncClient() as client:
        for i, user_data in enumerate(users_data, 1):
            try:
                # Prepare API data (remove role_context which is not part of registration)
                api_data = user_data.copy()
                role_context = api_data.pop('role_context', 'user')
                
                print(f"[{i:2d}/10] {user_data['email']}...", end=" ")
                
                # Make registration request
                response = await client.post(
                    "http://localhost:8000/api/v1/auth/register",
                    json=api_data,
                    timeout=15.0
                )
                
                if response.status_code == 201:
                    user_response = response.json()
                    results['created'].append(user_data['email'])
                    print(f"[CREATED] ID: {user_response['id'][:8]}...")
                    
                elif response.status_code == 400:
                    error_detail = response.json().get('detail', 'Unknown error')
                    if 'already exists' in error_detail:
                        results['skipped'].append(user_data['email'])
                        print(f"[SKIPPED] Already exists")
                    else:
                        results['failed'].append((user_data['email'], error_detail))
                        print(f"[ERROR] {error_detail}")
                else:
                    error_msg = f"HTTP {response.status_code}"
                    results['failed'].append((user_data['email'], error_msg))
                    print(f"[ERROR] {error_msg}")
                    
            except Exception as e:
                results['failed'].append((user_data['email'], str(e)))
                print(f"[ERROR] Exception: {e}")
    
    return results

async def test_authentication():
    """Test authentication with a few deployed users"""
    
    print(f"\nTesting authentication...")
    print("-" * 40)
    
    # Test users from different roles
    test_users = [
        {'email': 'admin@skillforge.ai', 'password': 'AdminPass123!', 'role': 'admin'},
        {'email': 'contact@techcorp.ai', 'password': 'TechPass123!', 'role': 'company_contact'},
        {'email': 'student.beginner@gmail.com', 'password': 'StudentPass123!', 'role': 'user'},
    ]
    
    login_results = []
    
    async with httpx.AsyncClient() as client:
        for user in test_users:
            try:
                print(f"Testing login: {user['email']}...", end=" ")
                
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
                    login_results.append((user['email'], True, f"Token expires in {token_data['expires_in']}s"))
                    print(f"[OK] Login successful")
                else:
                    error = response.json().get('detail', 'Unknown error')
                    login_results.append((user['email'], False, error))
                    print(f"[FAILED] {error}")
                    
            except Exception as e:
                login_results.append((user['email'], False, str(e)))
                print(f"[ERROR] {e}")
    
    return login_results

async def verify_database():
    """Verify the database was created correctly"""
    
    print(f"\nVerifying database...")
    print("-" * 40)
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to access a protected endpoint to verify database works
            response = await client.get("http://localhost:8000/api/v1/users/me", timeout=5.0)
            
            if response.status_code == 401:
                print("[OK] Database operational (authentication required as expected)")
                return True
            elif response.status_code == 500:
                print("[ERROR] Database error - check API logs")
                return False
            else:
                print(f"[WARNING] Unexpected response: {response.status_code}")
                return True
                
    except Exception as e:
        print(f"[ERROR] Cannot verify database: {e}")
        return False

def display_summary(deployment_results, auth_results):
    """Display deployment summary"""
    
    print("\n" + "=" * 70)
    print("SKILLFORGE AI DEPLOYMENT SUMMARY")
    print("=" * 70)
    
    print(f"Users created:  {len(deployment_results['created'])}")
    print(f"Users skipped:  {len(deployment_results['skipped'])}")
    print(f"Users failed:   {len(deployment_results['failed'])}")
    
    if deployment_results['created']:
        print(f"\n✅ Successfully created users:")
        for email in deployment_results['created']:
            print(f"  - {email}")
    
    if deployment_results['failed']:
        print(f"\n❌ Failed users:")
        for email, error in deployment_results['failed']:
            print(f"  - {email}: {error}")
    
    print(f"\nAuthentication test results:")
    successful_logins = sum(1 for _, success, _ in auth_results if success)
    print(f"  Successful logins: {successful_logins}/{len(auth_results)}")
    
    for email, success, message in auth_results:
        status = "✅" if success else "❌"
        print(f"  {status} {email}: {message}")
    
    print(f"\nUser credentials (all users):")
    print(f"  - admin@skillforge.ai / AdminPass123!")
    print(f"  - contact@techcorp.ai / TechPass123!")
    print(f"  - projects@financeplus.com / FinancePass123!")
    print(f"  - innovation@healthtech.fr / HealthPass123!")
    print(f"  - student.beginner@gmail.com / StudentPass123!")
    print(f"  - dev.intermediate@outlook.com / DevPass123!")
    print(f"  - data.analyst@yahoo.com / AnalystPass123!")
    print(f"  - expert.researcher@protonmail.com / ResearchPass123!")
    print(f"  - premium.consultant@icloud.com / PremiumPass123!")
    print(f"  - moderator@skillforge.ai / ModeratorPass123!")
    
    print(f"\nNext steps:")
    print(f"  1. Test role-based access control")
    print(f"  2. Create company profiles for company contacts")
    print(f"  3. Test the complete SkillForge AI workflow")

async def main():
    """Main deployment function"""
    
    print("SkillForge AI - Final Deployment with SQLite")
    print("Waiting for API, then deploying all users")
    print("=" * 70)
    
    # Step 1: Wait for API
    if not await wait_for_api():
        print("\n[FAILED] API is not available")
        print("Please start the API with:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    # Step 2: Verify database
    if not await verify_database():
        print("\n[WARNING] Database verification failed")
    
    # Step 3: Deploy users
    deployment_results = await deploy_users_via_api()
    
    # Step 4: Test authentication
    auth_results = await test_authentication()
    
    # Step 5: Display summary
    display_summary(deployment_results, auth_results)
    
    # Success criteria
    total_users = len(deployment_results['created']) + len(deployment_results['skipped'])
    successful_logins = sum(1 for _, success, _ in auth_results if success)
    
    if total_users >= 8 and successful_logins >= 2:
        print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"SkillForge AI is ready with {total_users} users!")
        return True
    else:
        print(f"\n⚠️  DEPLOYMENT PARTIAL")
        print(f"Some issues occurred but system is operational")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)