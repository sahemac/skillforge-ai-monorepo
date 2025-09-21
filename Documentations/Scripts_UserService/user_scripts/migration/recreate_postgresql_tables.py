#!/usr/bin/env python3
"""
Recréer les tables PostgreSQL avec les modèles définitifs
"""

import asyncio
import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def recreate_tables():
    """Recréer les tables PostgreSQL avec les modèles définitifs."""
    
    print("=" * 70)
    print("RECRÉATION DES TABLES POSTGRESQL")
    print("=" * 70)
    
    # Configuration PostgreSQL
    postgresql_url = "postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db"
    
    print("\\n[1/4] Suppression des tables existantes...")
    
    # Supprimer les tables avec psycopg2 (synchrone)
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='skillforge_db',
            user='skillforge_user',
            password='Psaumes@27'
        )
        cursor = conn.cursor()
        
        # Supprimer toutes les tables dans l'ordre inverse des dépendances
        tables_to_drop = [
            'company_subscriptions',
            'company_team_members', 
            'company_profiles',
            'user_sessions',
            'user_settings',
            'users'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                print(f"  [OK] Table {table} supprimée")
            except Exception as e:
                print(f"  [INFO] Table {table}: {e}")
        
        # Supprimer les types enum s'ils existent
        enum_types = ['userrole', 'userstatus', 'userskilllevel', 'industrytype', 'companysize']
        for enum_type in enum_types:
            try:
                cursor.execute(f"DROP TYPE IF EXISTS {enum_type} CASCADE;")
                print(f"  [OK] Type {enum_type} supprimé")
            except Exception as e:
                print(f"  [INFO] Type {enum_type}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("  [OK] Tables et types supprimés avec succès")
        
    except Exception as e:
        print(f"  [ERROR] Erreur lors de la suppression: {e}")
        print("  [INFO] On continue quand même avec la création...")
    
    print("\\n[2/4] Import des modèles définitifs...")
    from app.models.base import SQLModel
    from app.models.user import User, UserSettings, UserSession
    from app.models.company import CompanyProfile, TeamMember, Subscription
    print("  [OK] Modèles définitifs importés")
    
    print("\\n[3/4] Création du moteur SQLAlchemy...")
    engine = create_async_engine(postgresql_url, echo=True)
    print("  [OK] Moteur créé")
    
    print("\\n[4/4] Création des nouvelles tables...")
    async with engine.begin() as conn:
        # Supprimer toutes les tables si elles existent encore
        await conn.run_sync(SQLModel.metadata.drop_all)
        # Créer toutes les tables avec la nouvelle structure
        await conn.run_sync(SQLModel.metadata.create_all)
    
    await engine.dispose()
    print("  [OK] Nouvelles tables créées avec succès")
    
    print("\\n" + "=" * 70)
    print("TABLES POSTGRESQL RECRÉÉES AVEC SUCCÈS")
    print("=" * 70)
    print("\\nProchaines étapes:")
    print("1. Vérifier la nouvelle structure des tables")
    print("2. Créer les utilisateurs de test")
    print("3. Tester les endpoints")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(recreate_tables())
    sys.exit(0 if success else 1)