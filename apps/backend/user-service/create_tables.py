#!/usr/bin/env python3
"""
Script pour créer toutes les tables de la base de données
Utilise SQLModel pour créer les tables directement
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings
from app.models.base import SQLModel

# Import tous les modèles pour qu'ils soient enregistrés dans SQLModel.metadata
from app.models.user_simple import User, UserSettings, UserSession
from app.models.company_simple import CompanyProfile, TeamMember, Subscription

async def create_tables():
    """Créer toutes les tables définies dans les modèles SQLModel"""
    
    settings = get_settings()
    print(f"[DB] Connexion a la base de donnees: {settings.DATABASE_URL}")
    
    # Créer le moteur async
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # Pour voir les requêtes SQL
        future=True
    )
    
    try:
        # Créer toutes les tables
        print("[INFO] Creation des tables...")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("[SUCCESS] Tables creees avec succes!")
        
        # Vérifier les tables créées
        print("\n[INFO] Verification des tables creees:")
        async with engine.begin() as conn:
            # Récupérer la liste des tables
            if settings.DATABASE_URL.startswith("sqlite"):
                result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            else:
                result = await conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            
            tables = result.fetchall()
            print(f"Tables trouvées: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la creation des tables: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("[START] Demarrage de la creation des tables...")
    asyncio.run(create_tables())
    print("[DONE] Termine!")