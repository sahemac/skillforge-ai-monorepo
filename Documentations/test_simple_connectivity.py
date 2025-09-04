#!/usr/bin/env python3
"""
Simple diagnostic script for cloud-sql-proxy connectivity
No Unicode characters to avoid Windows console issues
"""

import asyncio
import socket
import subprocess
import sys
import time
from datetime import datetime

# Configuration for SkillForge AI
PROJECT_ID = "skillforge-ai-mvp-25"
REGION = "europe-west1" 
INSTANCE_NAME = "skillforge-pg-instance-staging"
DATABASE_NAME = "skillforge_db"
USERNAME = "skillforge_user"
PASSWORD = "Psaumes@27"

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 5432

print("DIAGNOSTIC CLOUD-SQL-PROXY - SKILLFORGE AI")
print("=" * 60)
print(f"Configuration:")
print(f"   Project: {PROJECT_ID}")
print(f"   Region: {REGION}")
print(f"   Instance: {INSTANCE_NAME}")
print(f"   Local: {LOCAL_HOST}:{LOCAL_PORT}")
print()

def test_port_listening():
    """Test 1: Check if port 5432 is listening"""
    print("1. Test port 5432 listening...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((LOCAL_HOST, LOCAL_PORT))
        sock.close()
        
        if result == 0:
            print("   SUCCESS Port 5432 is accessible")
            return True
        else:
            print("   ERROR Port 5432 is not accessible")
            print(f"   ERROR Connection result code: {result}")
            return False
    except Exception as e:
        print(f"   ERROR Port test failed: {e}")
        return False

def test_cloud_sql_proxy_process():
    """Test 2: Check if cloud-sql-proxy process is running"""
    print("\n2. Test cloud-sql-proxy process...")
    
    try:
        if sys.platform == "win32":
            # Windows task list
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq cloud_sql_proxy*"],
                capture_output=True,
                text=True
            )
            if "cloud_sql_proxy" in result.stdout:
                print("   SUCCESS cloud-sql-proxy process detected")
                # Extract PID if possible
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'cloud_sql_proxy' in line:
                        print(f"   INFO Process: {line.strip()}")
                return True
            else:
                print("   ERROR cloud-sql-proxy process not found")
                return False
        else:
            # Linux/Mac
            result = subprocess.run(
                ["pgrep", "-f", "cloud_sql_proxy"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("   SUCCESS cloud-sql-proxy process detected")
                print(f"   INFO Process IDs: {result.stdout.strip()}")
                return True
            else:
                print("   ERROR cloud-sql-proxy process not found")
                return False
        
    except Exception as e:
        print(f"   ERROR Process search failed: {e}")
        return False

def test_gcloud_auth():
    """Test 3: Check gcloud authentication"""
    print("\n3. Test gcloud authentication...")
    
    try:
        # Check gcloud installed
        result = subprocess.run(
            ["gcloud", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("   ERROR gcloud CLI not installed or not in PATH")
            return False
        
        print("   SUCCESS gcloud CLI installed")
        
        # Check authentication
        auth_result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if auth_result.stdout.strip():
            active_account = auth_result.stdout.strip()
            print(f"   SUCCESS Authenticated with: {active_account}")
            return True
        else:
            print("   ERROR No active gcloud account")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ERROR gcloud timeout (>10s)")
        return False
    except Exception as e:
        print(f"   ERROR gcloud error: {e}")
        return False

async def test_postgresql_connection():
    """Test 4: Test PostgreSQL connection"""
    print("\n4. Test PostgreSQL connection...")
    
    try:
        import asyncpg
        
        connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{LOCAL_HOST}:{LOCAL_PORT}/{DATABASE_NAME}"
        
        print(f"   INFO Attempting connection: postgresql://{USERNAME}:***@{LOCAL_HOST}:{LOCAL_PORT}/{DATABASE_NAME}")
        
        # Try connection with timeout
        conn = await asyncio.wait_for(
            asyncpg.connect(connection_string),
            timeout=10.0
        )
        
        # Test simple query
        result = await conn.fetchval("SELECT current_timestamp")
        await conn.close()
        
        print(f"   SUCCESS PostgreSQL connection successful")
        print(f"   INFO Server timestamp: {result}")
        return True
        
    except asyncio.TimeoutError:
        print("   ERROR PostgreSQL connection timeout (>10s)")
        return False
    except ImportError:
        print("   ERROR asyncpg module not available")
        return False
    except Exception as e:
        print(f"   ERROR PostgreSQL connection failed: {e}")
        return False

def show_cloud_sql_proxy_command():
    """Show the exact command to start cloud-sql-proxy"""
    print("\nCLOUD-SQL-PROXY COMMAND FOR PRIVATE INSTANCE")
    print("=" * 60)
    
    connection_name = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"
    
    print("IMPORTANT: This Cloud SQL instance uses PRIVATE IP only (no public IP)")
    print("You need to use one of these approaches:")
    print()
    
    print("OPTION 1 - Private IP mode (requires VPC access):")
    print(f"   cloud_sql_proxy -instances={connection_name}=tcp:{LOCAL_PORT} -ip_address_types=PRIVATE")
    print()
    
    print("OPTION 2 - Enable public IP temporarily via Terraform:")
    print("   Edit: terraform/environments/staging/database.tf")
    print("   Change: ipv4_enabled = false  ->  ipv4_enabled = true")
    print("   Run: terraform plan && terraform apply")
    print(f"   Then: cloud_sql_proxy -instances={connection_name}=tcp:{LOCAL_PORT}")
    print()
    
    print("OPTION 3 - Use from Cloud Run or GCE instance (recommended for production)")
    print("   Deploy your app to Cloud Run with VPC connector")
    print("   The private connection will work automatically")
    print()

def show_troubleshooting():
    """Show troubleshooting steps"""
    print("TROUBLESHOOTING STEPS")
    print("=" * 60)
    
    print("\n1. If cloud-sql-proxy not found:")
    print("   Install: gcloud components install cloud_sql_proxy")
    
    print("\n2. If authentication error:")
    print("   Run: gcloud auth login")
    print("   Run: gcloud auth application-default login")
    
    print("\n3. If port not accessible:")
    print("   Check cloud-sql-proxy is running")
    print("   Check firewall settings")
    print("   Try different port: -instances=...=tcp:5433")
    
    print("\n4. If PostgreSQL connection fails:")
    print("   Verify cloud-sql-proxy logs")
    print("   Check database credentials")
    print("   Verify instance name and region")

async def main():
    """Main diagnostic function"""
    start_time = time.time()
    
    # Sequential tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Port
    if test_port_listening():
        tests_passed += 1
    
    # Test 2: Process
    if test_cloud_sql_proxy_process():
        tests_passed += 1
    
    # Test 3: Auth
    if test_gcloud_auth():
        tests_passed += 1
    
    # Test 4: DB Connection
    if await test_postgresql_connection():
        tests_passed += 1
    
    # Results
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC RESULTS")
    print("=" * 60)
    print(f"Duration: {duration:.2f}s")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\nSUCCESS - All tests passed!")
        print("cloud-sql-proxy is working correctly")
        print("You can now run the full validation")
    else:
        print(f"\nERROR - {total_tests - tests_passed} test(s) failed")
        print("cloud-sql-proxy needs configuration")
        
        if tests_passed == 0:
            print("\nCRITICAL: cloud-sql-proxy not configured at all")
            show_cloud_sql_proxy_command()
        else:
            print("\nPARTIAL: some adjustments needed")
        
        show_troubleshooting()
    
    return 0 if tests_passed == total_tests else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\nCritical error: {e}")
        sys.exit(1)