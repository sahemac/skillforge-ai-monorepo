#!/usr/bin/env python3
"""
Test de différentes méthodes de connexion PostgreSQL
"""

import asyncio
import sys

async def test_asyncpg_localhost():
    """Test asyncpg avec localhost"""
    print("1. Test asyncpg avec localhost...")
    try:
        import asyncpg
        conn = await asyncio.wait_for(
            asyncpg.connect("postgresql://skillforge_user:Psaumes@27@localhost:5432/skillforge_db"),
            timeout=5.0
        )
        result = await conn.fetchval("SELECT 'asyncpg localhost OK'")
        await conn.close()
        print(f"   SUCCESS: {result}")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

async def test_asyncpg_ip():
    """Test asyncpg avec IP"""
    print("\n2. Test asyncpg avec 127.0.0.1...")
    try:
        import asyncpg
        conn = await asyncio.wait_for(
            asyncpg.connect("postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"),
            timeout=5.0
        )
        result = await conn.fetchval("SELECT 'asyncpg IP OK'")
        await conn.close()
        print(f"   SUCCESS: {result}")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

async def test_asyncpg_params():
    """Test asyncpg avec paramètres séparés"""
    print("\n3. Test asyncpg avec paramètres séparés...")
    try:
        import asyncpg
        conn = await asyncio.wait_for(
            asyncpg.connect(
                host="localhost",
                port=5432,
                user="skillforge_user", 
                password="Psaumes@27",
                database="skillforge_db"
            ),
            timeout=5.0
        )
        result = await conn.fetchval("SELECT 'asyncpg params OK'")
        await conn.close()
        print(f"   SUCCESS: {result}")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_psycopg2():
    """Test avec psycopg2 synchrone"""
    print("\n4. Test psycopg2...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="skillforge_user",
            password="Psaumes@27", 
            database="skillforge_db",
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute("SELECT 'psycopg2 OK'")
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(f"   SUCCESS: {result}")
        return True
    except ImportError:
        print("   SKIP: psycopg2 non installé")
        return None
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_telnet_simulation():
    """Test connexion socket basique"""
    print("\n5. Test socket basique...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 5432))
        
        # Envoyer message de démarrage PostgreSQL simple
        sock.send(b'\x00\x03\x00\x00user\x00skillforge_user\x00database\x00skillforge_db\x00\x00')
        
        # Recevoir réponse
        response = sock.recv(100)
        sock.close()
        
        if response:
            print(f"   SUCCESS: Réponse du serveur ({len(response)} bytes)")
            return True
        else:
            print("   ERROR: Pas de réponse")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

async def main():
    print("TEST MÉTHODES DE CONNEXION POSTGRESQL")
    print("=" * 50)
    
    tests = [
        ("asyncpg localhost", test_asyncpg_localhost()),
        ("asyncpg IP", test_asyncpg_ip()), 
        ("asyncpg params", test_asyncpg_params()),
        ("psycopg2", test_psycopg2()),
        ("socket basique", test_telnet_simulation())
    ]
    
    results = []
    
    for name, test_func in tests:
        if asyncio.iscoroutine(test_func):
            result = await test_func
        else:
            result = test_func
        results.append((name, result))
    
    print(f"\n" + "=" * 50)
    print("RÉSULTATS:")
    
    success_count = 0
    for name, result in results:
        if result is True:
            print(f"✓ {name}: SUCCESS")
            success_count += 1
        elif result is False:
            print(f"✗ {name}: FAILED")
        else:
            print(f"- {name}: SKIPPED")
    
    print(f"\nTests réussis: {success_count}")
    
    if success_count > 0:
        print("\nAu moins une méthode fonctionne!")
        print("Utilisez la méthode qui marche pour la validation.")
    else:
        print("\nAucune méthode ne fonctionne.")
        print("Problème avec cloud-sql-proxy ou configuration.")

if __name__ == "__main__":
    asyncio.run(main())