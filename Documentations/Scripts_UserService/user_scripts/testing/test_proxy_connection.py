#!/usr/bin/env python3
"""
Simple test to check if Cloud SQL Proxy is running
"""

import socket
import asyncio
import asyncpg

def test_port_connection():
    """Test if port 5432 is accessible"""
    print("Testing port 5432 accessibility...")
    
    try:
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 5432))
        sock.close()
        
        if result == 0:
            print("[OK] Port 5432 is accessible")
            return True
        else:
            print(f"[ERROR] Port 5432 is not accessible (error: {result})")
            return False
            
    except Exception as e:
        print(f"[ERROR] Socket test failed: {e}")
        return False

async def test_postgresql_connection():
    """Test PostgreSQL connection via proxy"""
    print("\nTesting PostgreSQL connection...")
    
    connection_configs = [
        {
            'host': '127.0.0.1',
            'port': 5432,
            'database': 'skillforge_db', 
            'user': 'skillforge_user',
            'password': 'Psaumes@27'
        },
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'skillforge_db',
            'user': 'skillforge_user', 
            'password': 'Psaumes@27'
        }
    ]
    
    for i, config in enumerate(connection_configs, 1):
        try:
            print(f"\nAttempt {i}: {config['host']}:{config['port']}")
            
            conn = await asyncpg.connect(**config, timeout=5)
            
            # Test basic query
            db_name = await conn.fetchval('SELECT current_database();')
            user_name = await conn.fetchval('SELECT current_user;')
            
            print(f"[SUCCESS] Connected to database: {db_name}")
            print(f"[SUCCESS] Connected as user: {user_name}")
            
            await conn.close()
            return True, config
            
        except Exception as e:
            print(f"[FAILED] Connection {i}: {e}")
            continue
    
    return False, None

def main():
    """Main test function"""
    print("Cloud SQL Proxy Connection Test")
    print("=" * 40)
    
    # Test 1: Port accessibility
    port_ok = test_port_connection()
    
    # Test 2: PostgreSQL connection
    async def run_pg_test():
        return await test_postgresql_connection()
    
    pg_ok, working_config = asyncio.run(run_pg_test())
    
    print("\n" + "=" * 40)
    print("TEST RESULTS")
    print("=" * 40)
    
    print(f"Port 5432 accessible: {'YES' if port_ok else 'NO'}")
    print(f"PostgreSQL connection: {'YES' if pg_ok else 'NO'}")
    
    if pg_ok:
        print(f"\nWorking configuration:")
        print(f"  Host: {working_config['host']}")
        print(f"  Port: {working_config['port']}")
        print(f"  Database: {working_config['database']}")
        print(f"  User: {working_config['user']}")
        print("\n[READY] Cloud SQL Proxy is working correctly!")
        print("You can now start the user-service API and deploy users.")
        
    else:
        print("\n[NOT READY] Cloud SQL Proxy issues detected")
        print("\nTroubleshooting steps:")
        print("1. Check if Cloud SQL Proxy is still running")
        print("2. Verify the proxy command:")
        print("   cloud-sql-proxy.exe --port=5432 skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging")
        print("3. Check proxy output for errors")
        print("4. Restart proxy if needed")
    
    return pg_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)