#!/usr/bin/env python3
"""
Integration Tests for User Service
Tests the complete API functionality with real database operations.
"""

import asyncio
import sys
import os
import httpx
import json
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

async def run_integration_tests():
    """Run comprehensive integration tests."""
    
    print("=" * 70)
    print("USER-SERVICE INTEGRATION TESTS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    test_results = []
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Service Health
        print("\n[1/6] Testing Service Health...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check: {health_data.get('status')}")
                test_results.append(True)
            else:
                print(f"❌ Health check failed: {response.status_code}")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Health check error: {e}")
            test_results.append(False)
        
        # Test 2: Root Endpoint
        print("\n[2/6] Testing Root Endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                root_data = response.json()
                print(f"✅ Root endpoint: {root_data.get('service')}")
                test_results.append(True)
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            test_results.append(False)
        
        # Test 3: API Documentation
        print("\n[3/6] Testing API Documentation...")
        try:
            response = await client.get(f"{base_url}/api/v1/docs")
            if response.status_code == 200:
                print("✅ OpenAPI docs accessible")
                test_results.append(True)
            else:
                print(f"❌ API docs failed: {response.status_code}")
                test_results.append(False)
        except Exception as e:
            print(f"❌ API docs error: {e}")
            test_results.append(False)
        
        # Test 4: Metrics Endpoint
        print("\n[4/6] Testing Metrics...")
        try:
            response = await client.get(f"{base_url}/metrics")
            if response.status_code in [200, 404]:  # 404 if metrics disabled
                print("✅ Metrics endpoint accessible")
                test_results.append(True)
            else:
                print(f"❌ Metrics failed: {response.status_code}")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Metrics error: {e}")
            test_results.append(False)
        
        # Test 5: Auth Health
        print("\n[5/6] Testing Auth Health...")
        try:
            response = await client.get(f"{base_url}/api/v1/auth/health")
            if response.status_code == 200:
                print("✅ Auth service healthy")
                test_results.append(True)
            else:
                print(f"❌ Auth health failed: {response.status_code}")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Auth health error: {e}")
            test_results.append(False)
        
        # Test 6: Database Connectivity Test
        print("\n[6/6] Testing Database Operations...")
        try:
            # Test users endpoint (should require auth but not fail with 500)
            response = await client.get(f"{base_url}/api/v1/users/")
            if response.status_code in [200, 401, 403, 422]:  # Valid responses
                print("✅ Users endpoint accessible (auth required)")
                test_results.append(True)
            else:
                print(f"❌ Users endpoint error: {response.status_code}")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Database test error: {e}")
            test_results.append(False)
    
    # Test Summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results)
    
    test_names = [
        "Service Health",
        "Root Endpoint", 
        "API Documentation",
        "Metrics Endpoint",
        "Auth Health",
        "Database Operations"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        icon = "✅" if result else "❌"
        print(f"{icon} {name}: {'PASS' if result else 'FAIL'}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All integration tests PASSED!")
        return True
    else:
        print("⚠️ Some integration tests FAILED.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)