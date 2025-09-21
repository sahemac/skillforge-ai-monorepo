#!/usr/bin/env python3
"""
Diagnose Cloud SQL connection issues
Test different database names, users, and connection parameters
"""

import asyncio
import asyncpg
import socket

# Common database configurations to try
TEST_CONFIGS = [
    # Original configuration
    {
        'name': 'Original Config',
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'skillforge_db',
        'user': 'skillforge_user',
        'password': 'Psaumes@27'
    },
    # Alternative database names
    {
        'name': 'Default postgres DB',
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'postgres',
        'user': 'skillforge_user',
        'password': 'Psaumes@27'
    },
    # Alternative usernames
    {
        'name': 'Postgres user',
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'skillforge_db',
        'user': 'postgres',
        'password': 'Psaumes@27'
    },
    # Combined alternatives
    {
        'name': 'Postgres user + DB',
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Psaumes@27'
    },
    # Without password
    {
        'name': 'No password',
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'skillforge_db',
        'user': 'skillforge_user',
        'password': ''
    }
]

async def test_configuration(config):
    """Test a specific database configuration"""
    try:
        print(f"\nTesting: {config['name']}")
        print(f"  Host: {config['host']}:{config['port']}")
        print(f"  Database: {config['database']}")
        print(f"  User: {config['user']}")
        print(f"  Password: {'*' * len(config['password']) if config['password'] else 'None'}")
        
        # Remove 'name' from config for asyncpg
        connection_config = {k: v for k, v in config.items() if k != 'name'}
        conn = await asyncpg.connect(**connection_config, timeout=10)
        
        # Get basic info
        db_name = await conn.fetchval('SELECT current_database();')
        user_name = await conn.fetchval('SELECT current_user;')
        version = await conn.fetchval('SELECT version();')
        
        print(f"  [SUCCESS] Connected!")
        print(f"  Database: {db_name}")
        print(f"  User: {user_name}")
        print(f"  Version: {version[:50]}...")
        
        # List databases
        databases = await conn.fetch('SELECT datname FROM pg_database WHERE datistemplate = false;')
        print(f"  Available databases: {[db['datname'] for db in databases]}")
        
        # List tables if any
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        if tables:
            print(f"  Tables in {db_name}: {[t['tablename'] for t in tables]}")
        else:
            print(f"  No tables found in {db_name}")
        
        await conn.close()
        return True, config
        
    except Exception as e:
        print(f"  [FAILED] {str(e)}")
        return False, None

def test_network_connectivity():
    """Test basic network connectivity"""
    print("Network Connectivity Test")
    print("-" * 30)
    
    hosts_to_test = [
        ('127.0.0.1', 5432),
        ('localhost', 5432),
    ]
    
    for host, port in hosts_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"[OK] {host}:{port} - Port accessible")
            else:
                print(f"[ERROR] {host}:{port} - Port not accessible (code: {result})")
                
        except Exception as e:
            print(f"[ERROR] {host}:{port} - Exception: {e}")

async def main():
    """Main diagnostic function"""
    print("Cloud SQL Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Network connectivity
    test_network_connectivity()
    
    print(f"\nDatabase Connection Tests")
    print("-" * 30)
    
    # Test 2: Database configurations
    working_configs = []
    
    for config in TEST_CONFIGS:
        success, working_config = await test_configuration(config)
        if success:
            working_configs.append(working_config)
    
    # Summary
    print(f"\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if working_configs:
        print(f"[SUCCESS] Found {len(working_configs)} working configuration(s)!")
        
        for i, config in enumerate(working_configs, 1):
            print(f"\nWorking Config #{i}: {config['name']}")
            print(f"  Host: {config['host']}")
            print(f"  Port: {config['port']}")
            print(f"  Database: {config['database']}")
            print(f"  User: {config['user']}")
            print(f"  Password: {config['password']}")
        
        print(f"\nRecommendation:")
        print(f"Update your configuration files to use:")
        best_config = working_configs[0]
        print(f"  DATABASE_URL=postgresql+asyncpg://{best_config['user']}:{best_config['password']}@{best_config['host']}:{best_config['port']}/{best_config['database']}")
        
    else:
        print("[FAILED] No working configurations found!")
        print("\nPossible issues:")
        print("1. Cloud SQL Proxy is not running correctly")
        print("2. Wrong instance name in proxy command")
        print("3. Database/user doesn't exist")
        print("4. Authentication credentials are wrong")
        print("5. Network connectivity issues")
        
        print("\nNext steps:")
        print("1. Check Cloud SQL Proxy output for errors")
        print("2. Verify instance exists in Google Cloud Console")
        print("3. Check database users and permissions")
        print("4. Try connecting with different credentials")
    
    return len(working_configs) > 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)