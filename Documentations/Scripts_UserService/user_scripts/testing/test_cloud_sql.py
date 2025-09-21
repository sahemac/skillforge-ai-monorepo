#!/usr/bin/env python3
"""
Test de connexion PostgreSQL Cloud SQL avec différentes méthodes
"""

import psycopg2
import asyncpg
import asyncio
import os

def test_psycopg2_connection():
    """Test avec psycopg2 (synchrone)"""
    print("=== Test connexion psycopg2 ===")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="skillforge_db",
            user="skillforge_user",
            password="Psaumes@27"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Connexion psycopg2 réussie: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erreur psycopg2: {e}")
        return False

async def test_asyncpg_connection():
    """Test avec asyncpg (asynchrone)"""
    print("\n=== Test connexion asyncpg ===")
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="skillforge_db",
            user="skillforge_user",
            password="Psaumes@27"
        )
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connexion asyncpg réussie: {version[:50]}...")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Erreur asyncpg: {e}")
        return False

async def test_sqlalchemy_connection():
    """Test avec SQLAlchemy asyncpg"""
    print("\n=== Test connexion SQLAlchemy + asyncpg ===")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        engine = create_async_engine(
            "postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db",
            echo=False
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connexion SQLAlchemy réussie: {version[:50]}...")
        
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Erreur SQLAlchemy: {e}")
        return False

def test_simple_connection():
    """Test de connexion très simple"""
    print("\n=== Test connexion simple ===")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("✅ Port 5432 accessible")
            return True
        else:
            print(f"❌ Port 5432 inaccessible: {result}")
            return False
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
        return False

async def main():
    print("Test de connexion PostgreSQL Cloud SQL")
    print("=" * 50)
    
    # Test socket simple
    test_simple_connection()
    
    # Test psycopg2
    test_psycopg2_connection()
    
    # Test asyncpg
    await test_asyncpg_connection()
    
    # Test SQLAlchemy
    await test_sqlalchemy_connection()

if __name__ == "__main__":
    asyncio.run(main())