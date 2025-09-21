#!/usr/bin/env python3
"""
Production Service Validation Script
Validates that the user-service is running correctly with all components.
"""

import asyncio
import sys
import os
import httpx
import time
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

async def validate_service():
    """Comprehensive service validation."""
    
    print("=" * 70)
    print("SKILLFORGE USER-SERVICE VALIDATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Health Check
    print("\n[1/5] Health Check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=10.0)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Service healthy: {health_data.get('status')}")
                results['health'] = True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                results['health'] = False
    except Exception as e:
        print(f"X Health check error: {e}")
        results['health'] = False
    
    # Test 2: Database Connection
    print("\n[2/5] Database Connection...")
    try:
        from app.core.database import check_db_connection
        db_ok = await check_db_connection()
        if db_ok:
            print("✅ Database connection successful")
            results['database'] = True
        else:
            print("❌ Database connection failed")
            results['database'] = False
    except Exception as e:
        print(f"❌ Database error: {e}")
        results['database'] = False
    
    # Test 3: Cache Service
    print("\n[3/5] Cache Service...")
    try:
        from app.core.cache import cache_service
        if cache_service.is_connected:
            print("✅ Redis cache connected")
            results['cache'] = True
        else:
            print("⚠️ Redis cache not available (optional)")
            results['cache'] = False
    except Exception as e:
        print(f"⚠️ Cache check error: {e}")
        results['cache'] = False
    
    # Test 4: API Endpoints
    print("\n[4/5] API Endpoints...")
    endpoints_to_test = [
        ("/", "GET"),
        ("/api/v1/auth/health", "GET"),
        ("/metrics", "GET"),
    ]
    
    endpoint_results = []
    async with httpx.AsyncClient() as client:
        for endpoint, method in endpoints_to_test:
            try:
                response = await client.request(method, f"http://localhost:8000{endpoint}", timeout=5.0)
                if response.status_code < 500:  # Allow 4xx for protected endpoints
                    print(f"✅ {method} {endpoint}: {response.status_code}")
                    endpoint_results.append(True)
                else:
                    print(f"❌ {method} {endpoint}: {response.status_code}")
                    endpoint_results.append(False)
            except Exception as e:
                print(f"❌ {method} {endpoint}: {e}")
                endpoint_results.append(False)
    
    results['endpoints'] = all(endpoint_results)
    
    # Test 5: Models and Migrations
    print("\n[5/5] Database Models...")
    try:
        from app.models import User, Company
        from app.core.database import get_async_session
        
        async with get_async_session() as session:
            # Simple count query to verify tables exist
            from sqlalchemy import text
            result = await session.execute(text("SELECT count(*) FROM users"))
            user_count = result.scalar()
            
            result = await session.execute(text("SELECT count(*) FROM companies"))
            company_count = result.scalar()
            
            print(f"✅ Users table: {user_count} records")
            print(f"✅ Companies table: {company_count} records")
            results['models'] = True
            
    except Exception as e:
        print(f"❌ Models validation error: {e}")
        results['models'] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component.capitalize()}: {'PASS' if status else 'FAIL'}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All validation tests PASSED! Service is ready for production.")
        return True
    else:
        print("⚠️ Some validation tests FAILED. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_service())
    sys.exit(0 if success else 1)