#!/usr/bin/env python3
"""
Simple Service Validation Script - No Unicode
Validates that the user-service is running correctly.
"""

import asyncio
import sys
import os
import httpx
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

async def simple_validate():
    """Simple service validation without Unicode characters."""
    
    print("=" * 60)
    print("USER-SERVICE SIMPLE VALIDATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health Check
    print("\n[1/4] Health Check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=10.0)
            if response.status_code == 200:
                health_data = response.json()
                print(f"OK Service healthy: {health_data.get('status')}")
                results['health'] = True
            else:
                print(f"FAIL Health check failed: {response.status_code}")
                results['health'] = False
    except Exception as e:
        print(f"FAIL Health check error: {e}")
        results['health'] = False
    
    # Test 2: API Endpoints
    print("\n[2/4] API Endpoints...")
    endpoints_to_test = [
        ("/", "GET"),
        ("/api/v1/auth/health", "GET"),
    ]
    
    endpoint_results = []
    async with httpx.AsyncClient() as client:
        for endpoint, method in endpoints_to_test:
            try:
                response = await client.request(method, f"http://localhost:8000{endpoint}", timeout=5.0)
                if response.status_code < 500:  # Allow 4xx for protected endpoints
                    print(f"OK {method} {endpoint}: {response.status_code}")
                    endpoint_results.append(True)
                else:
                    print(f"FAIL {method} {endpoint}: {response.status_code}")
                    endpoint_results.append(False)
            except Exception as e:
                print(f"FAIL {method} {endpoint}: {e}")
                endpoint_results.append(False)
    
    results['endpoints'] = all(endpoint_results)
    
    # Test 3: Database Models
    print("\n[3/4] Database Models...")
    try:
        from app.models import User
        # CompanyProfile moved to company-service
        from app.core.database import get_async_session
        
        async with get_async_session() as session:
            # Simple count query to verify tables exist
            from sqlalchemy import text
            result = await session.execute(text("SELECT count(*) FROM users"))
            user_count = result.scalar()
            
            result = await session.execute(text("SELECT count(*) FROM company_profiles"))
            company_count = result.scalar()
            
            print(f"OK Users table: {user_count} records")
            print(f"OK Company profiles table: {company_count} records")
            results['models'] = True
            
    except Exception as e:
        print(f"FAIL Models validation error: {e}")
        results['models'] = False
    
    # Test 4: Basic API Response
    print("\n[4/4] API Response Test...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                data = response.json()
                print(f"OK Root endpoint response: {data.get('service', 'N/A')}")
                results['api'] = True
            else:
                print(f"FAIL Root endpoint: {response.status_code}")
                results['api'] = False
    except Exception as e:
        print(f"FAIL API test error: {e}")
        results['api'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for component, status in results.items():
        icon = "PASS" if status else "FAIL"
        print(f"{icon} {component.capitalize()}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("SUCCESS: All validation tests PASSED!")
        return True
    else:
        print("WARNING: Some validation tests FAILED.")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_validate())
    sys.exit(0 if success else 1)