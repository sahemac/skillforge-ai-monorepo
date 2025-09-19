#!/usr/bin/env python3
"""
Script pour migrer de SQLite vers PostgreSQL
Une fois que Cloud SQL Proxy fonctionne
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings
from app.models.base import SQLModel

# Import tous les modèles
from app.models.user_simple import User, UserSettings, UserSession
from app.models.company_simple import CompanyProfile, TeamMember, Subscription

async def test_postgresql_connection():
    """Tester la connexion PostgreSQL"""
    
    # Configuration PostgreSQL
    postgresql_url = "postgresql+asyncpg://skillforge_user:Psaumes%4027@localhost:5432/skillforge_db"
    
    print(f"[TEST] Test de connexion PostgreSQL: {postgresql_url}")
    
    try:
        # Créer le moteur
        engine = create_async_engine(postgresql_url, echo=False)
        
        # Tester la connexion
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"[SUCCESS] PostgreSQL connecté: {version}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Impossible de se connecter à PostgreSQL: {e}")
        print("[INFO] Assurez-vous que Cloud SQL Proxy fonctionne:")
        print("  cloud-sql-proxy.exe --port=5432 skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging")
        return False

async def create_tables_postgresql():
    """Créer les tables dans PostgreSQL"""
    
    postgresql_url = "postgresql+asyncpg://skillforge_user:Psaumes%4027@localhost:5432/skillforge_db"
    
    print(f"[INFO] Création des tables PostgreSQL...")
    
    try:
        engine = create_async_engine(postgresql_url, echo=True)
        
        # Créer toutes les tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("[SUCCESS] Tables PostgreSQL créées avec succès!")
        
        # Vérifier les tables
        async with engine.begin() as conn:
            result = await conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = result.fetchall()
            print(f"[INFO] Tables trouvées: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création des tables: {e}")
        return False

async def main():
    """Fonction principale"""
    
    print("[START] Migration vers PostgreSQL...")
    
    # 1. Tester la connexion
    if not await test_postgresql_connection():
        print("[ABORT] Migration avortée - pas de connexion PostgreSQL")
        return False
    
    # 2. Créer les tables
    if not await create_tables_postgresql():
        print("[ABORT] Migration avortée - erreur création tables")
        return False
    
    print("[SUCCESS] Migration vers PostgreSQL terminée!")
    print("\n[NEXT] Pour utiliser PostgreSQL:")
    print("1. Vérifiez que le fichier .env pointe vers PostgreSQL")
    print("2. Relancez vos tests avec la nouvelle base")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("[DONE] Migration réussie!")
    else:
        print("[FAILED] Migration échouée!")