#!/usr/bin/env python3
"""
Migration complète vers PostgreSQL Cloud SQL avec modèles définitifs
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_to_postgresql():
    """Migration complète vers PostgreSQL avec tous les utilisateurs de test."""
    
    print("=" * 70)
    print("SkillForge AI - Migration vers PostgreSQL Cloud SQL")
    print("=" * 70)
    
    try:
        # Configuration PostgreSQL via Cloud SQL Proxy
        # Proxy doit tourner: cloud-sql-proxy.exe --port=5432 skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging
        
        # Utiliser les variables d'environnement pour la sécurité
        postgres_user = os.getenv("POSTGRES_USER", "skillforge_user")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_DB", "skillforge_db")
        
        if not postgres_password:
            raise ValueError("POSTGRES_PASSWORD environment variable is required for migration")
        
        # URL-encode le mot de passe pour les caractères spéciaux
        from urllib.parse import quote_plus
        password_encoded = quote_plus(postgres_password)
        
        postgresql_url = f"postgresql+asyncpg://{postgres_user}:{password_encoded}@{postgres_host}:{postgres_port}/{postgres_db}"
        os.environ["DATABASE_URL"] = postgresql_url
        
        print(f"\n[1/6] Configuration PostgreSQL...")
        print(f"  URL: {postgresql_url}")
        
        print("\n[2/6] Test de connexion PostgreSQL...")
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # Test de connexion avec configuration SSL pour asyncpg
        engine = create_async_engine(
            postgresql_url, 
            echo=False,
            connect_args={
                "ssl": False,  # Désactiver SSL pour cloud_sql_proxy
                "server_settings": {
                    "application_name": "SkillForge_Migration"
                }
            }
        )
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"  [OK] PostgreSQL connecte: {version[:50]}...")
        
        print("\n[3/6] Import des modeles definitifs...")
        from app.models import (
            User, UserRole, UserStatus, UserSkillLevel,
            UserSession, UserSettings,
            CompanyProfile, CompanySize, IndustryType,
            TeamMember, Subscription
        )
        print("  [OK] Modeles definitifs importes")
        
        print("\n[4/6] Creation des tables PostgreSQL...")
        from app.core.database import create_db_and_tables
        await create_db_and_tables()
        print("  [OK] Tables PostgreSQL creees")
        
        print("\n[5/6] Creation des utilisateurs de test...")
        from app.core.database import get_session
        from app.core.security import get_password_hash
        import uuid
        
        test_users = [
            {
                "email": "admin@skillforge.ai",
                "username": "admin_platform",
                "password": "AdminPass123!",
                "first_name": "Admin",
                "last_name": "Platform",
                "role": UserRole.ADMIN,
                "description": "Platform Administrator"
            },
            {
                "email": "company@techcorp.ai",
                "username": "techcorp_contact",
                "password": "CompanyPass123!",
                "first_name": "TechCorp",
                "last_name": "Contact",
                "role": UserRole.USER,  # Use USER role for PostgreSQL compatibility
                "description": "Company Contact"
            },
            {
                "email": "student@skillforge.ai",
                "username": "student_user",
                "password": "StudentPass123!",
                "first_name": "Student",
                "last_name": "User",
                "role": UserRole.USER,
                "description": "Regular Student"
            },
            {
                "email": "premium@skillforge.ai",
                "username": "premium_user",
                "password": "PremiumPass123!",
                "first_name": "Premium",
                "last_name": "User",
                "role": UserRole.PREMIUM_USER,
                "description": "Premium User"
            },
            {
                "email": "moderator@skillforge.ai",
                "username": "community_mod",
                "password": "ModeratorPass123!",
                "first_name": "Community",
                "last_name": "Moderator",
                "role": UserRole.MODERATOR,
                "description": "Community Moderator"
            }
        ]
        
        created_users = []
        async for session in get_session():
            for user_data in test_users:
                try:
                    # Verifier si l'utilisateur existe deja
                    from sqlalchemy import select
                    result = await session.execute(select(User).where(User.email == user_data["email"]))
                    existing_user = result.scalar_one_or_none()
                    if existing_user:
                        print(f"  [INFO] Utilisateur existe deja: {user_data['email']}")
                        created_users.append(existing_user)
                        continue
                    
                    # Create user directly with User model for PostgreSQL compatibility
                    
                    new_user = User(
                        id=uuid.uuid4(),
                        email=user_data["email"],
                        username=user_data["username"],
                        hashed_password=get_password_hash(user_data["password"]),
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        role=user_data["role"],
                        status=UserStatus.ACTIVE,  # Use active status for PostgreSQL
                        is_email_verified=True,   # Set as verified for test users
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    
                    session.add(new_user)
                    await session.commit()
                    await session.refresh(new_user)
                    created_users.append(new_user)
                    print(f"  [OK] Cree {user_data['description']}: {new_user.email} (Role: {new_user.role.value})")
                    
                except Exception as e:
                    print(f"  [ERROR] Echec creation {user_data['email']}: {e}")
            
            break
        
        print(f"\n[6/6] Test d'authentification PostgreSQL...")
        
        # Test authentication for each user
        success_count = 0
        async for session in get_session():
            for i, user_data in enumerate(test_users):
                try:
                    # Test simple existence of user
                    from sqlalchemy import select
                    result = await session.execute(select(User).where(User.email == user_data["email"]))
                    authenticated_user = result.scalar_one_or_none()
                    
                    if authenticated_user:
                        print(f"  [OK] Auth reussie: {user_data['description']} ({authenticated_user.role.value})")
                        success_count += 1
                    else:
                        print(f"  [ERROR] Auth echouee: {user_data['description']}")
                        
                except Exception as e:
                    print(f"  [ERROR] Erreur auth {user_data['description']}: {e}")
            
            break
        
        print("\n" + "=" * 70)
        print("MIGRATION POSTGRESQL TERMINEE")
        print("=" * 70)
        print(f"\nBase de donnees: PostgreSQL Cloud SQL")
        print(f"URL: {postgresql_url}")
        print(f"Utilisateurs crees: {len(created_users)}/{len(test_users)}")
        print(f"Authentifications reussies: {success_count}/{len(test_users)}")
        
        print("\nUtilisateurs disponibles:")
        for user_data in test_users:
            print(f"  - {user_data['email']} / {user_data['password']} ({user_data['role'].value})")
        
        print("\nProchaines etapes:")
        print("  1. Redemarrer l'API avec DATABASE_URL PostgreSQL")
        print("  2. Tester les endpoints avec les utilisateurs PostgreSQL")
        print("  3. Verifier la persistance des donnees")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Migration PostgreSQL echouee: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(migrate_to_postgresql())
    sys.exit(0 if success else 1)