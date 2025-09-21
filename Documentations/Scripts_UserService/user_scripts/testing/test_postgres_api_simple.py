#!/usr/bin/env python3
"""
Test simple des endpoints API PostgreSQL avec les utilisateurs existants
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_postgresql_users():
    """Tester la presence des utilisateurs PostgreSQL."""
    
    print("=" * 70)
    print("TEST DES UTILISATEURS POSTGRESQL")
    print("=" * 70)
    
    # Force PostgreSQL connection
    postgresql_url = "postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db"
    os.environ["DATABASE_URL"] = postgresql_url
    
    try:
        print("\n[1/3] Configuration PostgreSQL...")
        print(f"URL: {postgresql_url}")
        
        print("\n[2/3] Test de connexion avec SQLAlchemy...")
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # Configuration comme dans migrate_to_postgresql.py qui fonctionne
        engine = create_async_engine(
            postgresql_url, 
            echo=False,
            connect_args={
                "ssl": False,
                "server_settings": {
                    "application_name": "SkillForge_Test"
                }
            }
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"PostgreSQL version: {version[:50]}...")
        
        print("\n[3/3] Verification des utilisateurs...")
        from app.models import User
        from app.core.database import get_session
        from sqlalchemy import select
        
        async for session in get_session():
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"Utilisateurs trouves: {len(users)}")
            for user in users:
                print(f"  - {user.email} ({user.role.value}) - Active: {user.is_active}")
            
            break
        
        await engine.dispose()
        
        print("\nPostgreSQL connection OK!")
        print("Utilisateurs disponibles pour tests API:")
        print("  - admin@skillforge.ai / AdminPass123!")
        print("  - company@techcorp.ai / CompanyPass123!")
        print("  - student@skillforge.ai / StudentPass123!")
        print("  - premium@skillforge.ai / PremiumPass123!")
        print("  - moderator@skillforge.ai / ModeratorPass123!")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_postgresql_users())
    print("\nLancement de l'API avec PostgreSQL:")
    print('DATABASE_URL="postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db" uvicorn app.main:app --port 8001 --reload')
    sys.exit(0 if success else 1)