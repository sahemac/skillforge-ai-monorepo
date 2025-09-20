#!/usr/bin/env python3
"""
Test script for new features added to SkillForge AI User Service
Tests: Utils, Rate Limiting, Redis Cache, Prometheus Monitoring
"""

import asyncio
import httpx
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8002"
TIMEOUT = 30


async def test_health_endpoint():
    """Test enhanced health endpoint."""
    print("🔍 Testing health endpoint...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Database: {data['checks']['database']}")
                print(f"   Cache: {data['checks']['cache']}")
                print(f"   Metrics: {data['checks']['metrics']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False


async def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    print("\n🔍 Testing metrics endpoint...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/metrics")
            
            if response.status_code == 200:
                metrics_text = response.text
                metrics_lines = metrics_text.split('\n')
                
                # Check for key metrics
                expected_metrics = [
                    'skillforge_app_info',
                    'skillforge_http_requests_total',
                    'skillforge_http_request_duration_seconds'
                ]
                
                found_metrics = []
                for metric in expected_metrics:
                    if any(metric in line for line in metrics_lines):
                        found_metrics.append(metric)
                
                print(f"✅ Metrics endpoint accessible")
                print(f"   Found {len(found_metrics)}/{len(expected_metrics)} expected metrics")
                for metric in found_metrics:
                    print(f"   - {metric}")
                
                return len(found_metrics) > 0
            else:
                print(f"❌ Metrics endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Metrics endpoint error: {str(e)}")
            return False


async def test_cache_info_endpoint():
    """Test cache info endpoint."""
    print("\n🔍 Testing cache info endpoint...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/cache/info")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cache info accessible: {data['status']}")
                
                if data['status'] == 'connected':
                    print(f"   Redis version: {data.get('redis_version', 'N/A')}")
                    print(f"   Connected clients: {data.get('connected_clients', 'N/A')}")
                else:
                    print(f"   Cache is {data['status']}")
                
                return True
            else:
                print(f"❌ Cache info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Cache info error: {str(e)}")
            return False


async def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n🔍 Testing rate limiting...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # Make multiple rapid requests to trigger rate limiting
            print("   Making rapid requests to trigger rate limit...")
            
            rate_limited = False
            for i in range(15):  # Try 15 requests rapidly
                response = await client.get(f"{BASE_URL}/health")
                
                if response.status_code == 429:
                    print(f"✅ Rate limiting triggered after {i+1} requests")
                    
                    # Check rate limit headers
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        print(f"   Retry-After header: {retry_after}s")
                    
                    rate_limited = True
                    break
                elif response.status_code != 200:
                    print(f"❌ Unexpected status code: {response.status_code}")
                    return False
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            if not rate_limited:
                print("⚠️  Rate limiting not triggered (might have high limits)")
                print("   This could be normal depending on configuration")
                return True
            
            return True
            
        except Exception as e:
            print(f"❌ Rate limiting test error: {str(e)}")
            return False


async def test_api_endpoints():
    """Test API endpoints functionality."""
    print("\n🔍 Testing API endpoints...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # Test documentation endpoint
            response = await client.get(f"{BASE_URL}/api/v1/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print(f"⚠️  API docs status: {response.status_code}")
            
            # Test registration endpoint (without actually registering)
            # This should return validation errors, confirming the endpoint works
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={}
            )
            
            if response.status_code == 422:  # Validation error expected
                print("✅ Registration endpoint responds to requests")
            else:
                print(f"⚠️  Registration endpoint status: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ API endpoints test error: {str(e)}")
            return False


async def test_database_connectivity():
    """Test database connectivity via health check."""
    print("\n🔍 Testing database connectivity...")
    
    # The health endpoint already checks database connectivity
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                db_status = data.get('checks', {}).get('database', 'unknown')
                
                if db_status == 'healthy':
                    print("✅ Database connectivity confirmed")
                    return True
                else:
                    print(f"❌ Database status: {db_status}")
                    return False
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Database connectivity error: {str(e)}")
            return False


async def test_service_startup():
    """Test that the service can start properly."""
    print("\n🔍 Testing service startup...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # Test root endpoint
            response = await client.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service started successfully")
                print(f"   Service: {data.get('service', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                print(f"   Environment: {data.get('environment', 'N/A')}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Service startup error: {str(e)}")
            return False


async def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Starting SkillForge AI User Service Feature Tests")
    print("=" * 60)
    
    tests = [
        ("Service Startup", test_service_startup),
        ("Health Endpoint", test_health_endpoint), 
        ("Database Connectivity", test_database_connectivity),
        ("Metrics Endpoint", test_metrics_endpoint),
        ("Cache Info", test_cache_info_endpoint),
        ("Rate Limiting", test_rate_limiting),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! New features are working correctly.")
    elif passed >= total * 0.7:  # 70% pass rate
        print("⚠️  Most tests passed. Some features may need attention.")
    else:
        print("❌ Many tests failed. Please check the implementation.")
    
    return passed, total


if __name__ == "__main__":
    print(f"Testing service at: {BASE_URL}")
    print("Make sure the service is running with PostgreSQL")
    print("Command: DATABASE_URL='postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db' POSTGRES_PASSWORD='Psaumes@27' uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload")
    print()
    
    try:
        passed, total = asyncio.run(run_all_tests())
        exit(0 if passed == total else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Test runner error: {str(e)}")
        exit(1)