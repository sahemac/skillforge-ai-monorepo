#!/usr/bin/env python3
"""
Copier les utilisateurs PostgreSQL vers SQLite pour les tests API
"""

import asyncio
import os
import sys
import psycopg2
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def copy_postgresql_to_sqlite():
    """Copier les utilisateurs de PostgreSQL vers SQLite."""
    
    print("=" * 70)
    print("COPIE DES UTILISATEURS POSTGRESQL VERS SQLITE")
    print("=" * 70)
    
    try:
        print("\n[1/4] Connexion à PostgreSQL...")
        
        # Connexion PostgreSQL avec psycopg2
        pg_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='skillforge_db',
            user='skillforge_user',
            password='Psaumes@27'
        )
        pg_cursor = pg_conn.cursor()
        
        # Récupérer tous les utilisateurs PostgreSQL
        pg_cursor.execute("""
            SELECT email, username, hashed_password, first_name, last_name, 
                   role, status, is_email_verified, is_active, experience_level,
                   country, timezone, language_preference, newsletter_subscribed,
                   created_at, updated_at
            FROM users
        """)
        
        postgresql_users = pg_cursor.fetchall()
        print(f"  ✅ {len(postgresql_users)} utilisateurs trouvés dans PostgreSQL")
        
        pg_cursor.close()
        pg_conn.close()
        
        print("\n[2/4] Configuration SQLite...")
        
        # Configuration SQLite pour l'API
        sqlite_url = "sqlite+aiosqlite:///./skillforge_dev.db"
        os.environ["DATABASE_URL"] = sqlite_url
        
        print(f"  📊 Base SQLite: ./skillforge_dev.db")
        
        print("\n[3/4] Import des modèles et création des tables SQLite...")
        
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.pool import StaticPool
        from app.models.base import SQLModel
        from app.models import User, UserRole, UserStatus, UserSkillLevel
        import uuid
        
        # Créer moteur SQLite
        engine = create_async_engine(
            sqlite_url,
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        # Créer les tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("  ✅ Tables SQLite créées")
        
        print("\n[4/4] Copie des utilisateurs vers SQLite...")
        
        from app.core.database import get_session
        
        copied_users = 0
        async for session in get_session():
            for pg_user in postgresql_users:
                try:
                    # Mapping des données PostgreSQL
                    email, username, hashed_password, first_name, last_name, \
                    role, status, is_email_verified, is_active, experience_level, \
                    country, timezone, language_preference, newsletter_subscribed, \
                    created_at, updated_at = pg_user
                    
                    # Créer l'utilisateur SQLite
                    sqlite_user = User(
                        id=uuid.uuid4(),
                        email=email,
                        username=username,
                        hashed_password=hashed_password,
                        first_name=first_name,
                        last_name=last_name,
                        role=UserRole(role),
                        status=UserStatus(status) if status else UserStatus.ACTIVE,
                        is_email_verified=is_email_verified if is_email_verified is not None else True,
                        is_active=is_active if is_active is not None else True,
                        experience_level=UserSkillLevel(experience_level) if experience_level else UserSkillLevel.BEGINNER,
                        country=country,
                        timezone=timezone or "UTC",
                        language_preference=language_preference or "en",
                        newsletter_subscribed=newsletter_subscribed if newsletter_subscribed is not None else True,
                        created_at=created_at or datetime.utcnow(),
                        updated_at=updated_at or datetime.utcnow()
                    )
                    
                    session.add(sqlite_user)
                    await session.commit()
                    await session.refresh(sqlite_user)
                    
                    print(f"  ✅ Copié: {email} ({role})")
                    copied_users += 1
                    
                except Exception as e:
                    print(f"  ❌ Erreur copie {email if 'email' in locals() else 'unknown'}: {e}")
                    await session.rollback()
            
            break
        
        await engine.dispose()
        
        print("\n" + "=" * 70)
        print("COPIE TERMINÉE")
        print("=" * 70)
        print(f"\nUtilisateurs copiés: {copied_users}/{len(postgresql_users)}")
        print(f"Base SQLite: ./skillforge_dev.db")
        
        if copied_users > 0:
            print("\n🎉 COPIE RÉUSSIE!")
            print("\nUtilisateurs disponibles dans SQLite:")
            for pg_user in postgresql_users:
                email, username, _, _, _, role, _, _, _, _, _, _, _, _, _, _ = pg_user
                print(f"  - {email} / AdminPass123! ({role})")
            
            print("\nPour tester l'API avec SQLite:")
            print('DATABASE_URL="sqlite+aiosqlite:///./skillforge_dev.db" uvicorn app.main:app --reload')
            
            return True
        else:
            print("\n❌ COPIE ÉCHOUÉE")
            return False
    
    except Exception as e:
        print(f"\n❌ Erreur de copie: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(copy_postgresql_to_sqlite())
    sys.exit(0 if success else 1)