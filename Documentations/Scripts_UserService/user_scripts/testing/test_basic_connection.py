#!/usr/bin/env python3
"""
Test de base pour vérifier si l'instance Cloud SQL répond
"""

import asyncio
import asyncpg
import psycopg2

def test_psycopg2_connection():
    """Test avec psycopg2 (synchrone)"""
    print("Testing with psycopg2 (synchronous)...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            database='postgres',  # Base par défaut
            user='postgres',      # User par défaut
            password='',          # Pas de mot de passe
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        
        print(f"[SUCCESS] psycopg2 connection works!")
        print(f"Version: {version[:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FAILED] psycopg2: {e}")
        return False

def test_telnet_equivalent():
    """Test de connexion TCP brute"""
    import socket
    
    print("\nTesting raw TCP connection...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 5432))
        
        # Envoyer un message PostgreSQL basique
        sock.send(b'\x00\x00\x00\x08\x04\xd2\x16\x2f')  # SSL request
        response = sock.recv(1024)
        
        print(f"[SUCCESS] TCP connection established")
        print(f"Response length: {len(response)} bytes")
        print(f"Response: {response}")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"[FAILED] TCP connection: {e}")
        return False

async def test_asyncpg_minimal():
    """Test asyncpg minimal"""
    print("\nTesting asyncpg with minimal config...")
    
    configs = [
        {'host': '127.0.0.1', 'port': 5432, 'user': 'postgres'},
        {'host': '127.0.0.1', 'port': 5432, 'database': 'postgres'},
        {'host': '127.0.0.1', 'port': 5432},
    ]
    
    for i, config in enumerate(configs, 1):
        try:
            print(f"  Attempt {i}: {config}")
            conn = await asyncpg.connect(**config, timeout=10)
            
            result = await conn.fetchval('SELECT 1;')
            print(f"  [SUCCESS] Minimal asyncpg works! Result: {result}")
            
            await conn.close()
            return True
            
        except Exception as e:
            print(f"  [FAILED] Attempt {i}: {e}")
            continue
    
    return False

def main():
    """Test principal"""
    print("Cloud SQL Basic Connection Test")
    print("=" * 40)
    
    # Test 1: TCP brut
    tcp_ok = test_telnet_equivalent()
    
    # Test 2: psycopg2
    psycopg2_ok = test_psycopg2_connection()
    
    # Test 3: asyncpg minimal
    asyncpg_ok = asyncio.run(test_asyncpg_minimal())
    
    print("\n" + "=" * 40)
    print("BASIC CONNECTION TEST RESULTS")
    print("=" * 40)
    
    print(f"TCP Connection:     {'OK' if tcp_ok else 'FAILED'}")
    print(f"psycopg2:          {'OK' if psycopg2_ok else 'FAILED'}")
    print(f"asyncpg minimal:   {'OK' if asyncpg_ok else 'FAILED'}")
    
    if any([tcp_ok, psycopg2_ok, asyncpg_ok]):
        print("\n[INFO] At least one connection method works!")
        print("The issue might be with specific credentials or database names.")
    else:
        print("\n[ERROR] No connection methods work!")
        print("Possible issues:")
        print("1. Cloud SQL instance is not running")
        print("2. Network connectivity issues")
        print("3. Proxy configuration problems")
    
    return any([tcp_ok, psycopg2_ok, asyncpg_ok])

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)