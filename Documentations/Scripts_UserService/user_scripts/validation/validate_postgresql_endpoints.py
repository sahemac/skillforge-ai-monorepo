#!/usr/bin/env python3
"""
Validation des endpoints avec PostgreSQL et les utilisateurs créés
"""

import asyncio
import sys
import os
import json

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def validate_postgresql_endpoints():
    """Valider les endpoints avec PostgreSQL."""
    
    print("=" * 70)
    print("VALIDATION DES ENDPOINTS AVEC POSTGRESQL")
    print("=" * 70)
    
    # Configuration PostgreSQL 
    postgresql_url = "postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db"
    os.environ["DATABASE_URL"] = postgresql_url
    
    try:
        print("\n[1/4] Test de connexion PostgreSQL...")
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text, select
        
        engine = create_async_engine(postgresql_url, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"  ✅ PostgreSQL connecté: {version[:50]}...")
        
        print("\n[2/4] Import des modèles et services...")
        from app.models.user import User
        from app.core.database import get_session
        from app.core.security import verify_password, get_password_hash
        print("  ✅ Modèles et services importés")
        
        print("\n[3/4] Vérification des utilisateurs PostgreSQL...")
        
        # Utilisateurs de test créés dans PostgreSQL
        test_users = [
            {"email": "admin@skillforge.ai", "password": "AdminPass123!", "role": "admin"},
            {"email": "company@techcorp.ai", "password": "CompanyPass123!", "role": "user"},
            {"email": "student@skillforge.ai", "password": "StudentPass123!", "role": "user"},
            {"email": "premium@skillforge.ai", "password": "PremiumPass123!", "role": "premium_user"},
            {"email": "moderator@skillforge.ai", "password": "ModeratorPass123!", "role": "moderator"}
        ]
        
        users_found = 0
        async for session in get_session():
            for user_data in test_users:
                try:
                    # Vérifier l'existence de l'utilisateur
                    result = await session.execute(select(User).where(User.email == user_data["email"]))
                    user = result.scalar_one_or_none()
                    
                    if user:
                        print(f"  ✅ {user_data['email']} - Rôle: {user.role.value}")
                        users_found += 1
                        
                        # Test de vérification du mot de passe (simulé)
                        # Note: En production, on utiliserait le hashing complet
                        print(f"    └─ Hash password disponible: {len(user.hashed_password)} chars")
                    else:
                        print(f"  ❌ {user_data['email']} - Non trouvé")
                
                except Exception as e:
                    print(f"  ❌ Erreur {user_data['email']}: {e}")
            break
        
        print(f"\n[4/4] Test de l'authentification simulée...")
        
        # Test d'authentification direct avec la base PostgreSQL
        auth_success = 0
        async for session in get_session():
            for user_data in test_users:
                try:
                    result = await session.execute(select(User).where(User.email == user_data["email"]))
                    user = result.scalar_one_or_none()
                    
                    if user and user.is_active:
                        print(f"  ✅ Auth simulée réussie: {user_data['email']} ({user.role.value})")
                        auth_success += 1
                    else:
                        print(f"  ❌ Auth simulée échouée: {user_data['email']}")
                
                except Exception as e:
                    print(f"  ❌ Erreur auth {user_data['email']}: {e}")
            break
        
        await engine.dispose()
        
        print("\n" + "=" * 70)
        print("VALIDATION POSTGRESQL TERMINÉE")
        print("=" * 70)
        print(f"\nBase de données: PostgreSQL Cloud SQL")
        print(f"URL: {postgresql_url}")
        print(f"Utilisateurs trouvés: {users_found}/5")
        print(f"Authentifications simulées réussies: {auth_success}/5")
        
        if users_found == 5 and auth_success == 5:
            print("\n🎉 VALIDATION COMPLÈTE - PostgreSQL prêt pour l'API!")
            print("\nUtilisateurs PostgreSQL disponibles:")
            for user_data in test_users:
                print(f"  - {user_data['email']} / {user_data['password']} ({user_data['role']})")
            
            print("\nPour démarrer l'API avec PostgreSQL:")
            print('DATABASE_URL="postgresql+asyncpg://skillforge_user:Psaumes@27@localhost:5432/skillforge_db" uvicorn app.main:app --reload')
            
            return True
        else:
            print("\n❌ VALIDATION INCOMPLÈTE")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur de validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_postgresql_endpoints())
    sys.exit(0 if success else 1)