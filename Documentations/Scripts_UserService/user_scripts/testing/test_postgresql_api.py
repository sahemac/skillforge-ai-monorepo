#!/usr/bin/env python3
"""
Test des endpoints API avec les utilisateurs PostgreSQL
"""

import asyncio
import sys
import os
import requests
import json

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_postgresql_api():
    """Tester les endpoints API avec les utilisateurs PostgreSQL."""
    
    print("=" * 70)
    print("TEST DES ENDPOINTS API AVEC POSTGRESQL")
    print("=" * 70)
    
    # Configuration des utilisateurs PostgreSQL existants
    postgresql_users = [
        {"email": "admin@skillforge.ai", "password": "AdminPass123!", "role": "admin"},
        {"email": "company@techcorp.ai", "password": "CompanyPass123!", "role": "user"},
        {"email": "student@skillforge.ai", "password": "StudentPass123!", "role": "user"},
        {"email": "premium@skillforge.ai", "password": "PremiumPass123!", "role": "premium_user"},
        {"email": "moderator@skillforge.ai", "password": "ModeratorPass123!", "role": "moderator"}
    ]
    
    # URLs des APIs - on teste sur le port 8000 qui utilise SQLite d'abord
    api_base_url = "http://localhost:8000"
    
    print(f"\n[1/4] Test de connectivité API sur {api_base_url}...")
    
    try:
        # Test du health check
        response = requests.get(f"{api_base_url}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ API accessible")
            health_data = response.json()
            print(f"  📊 Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"  ❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur de connexion API: {e}")
        return False
    
    print(f"\n[2/4] Test des endpoints d'authentification...")
    
    auth_success = 0
    tokens = {}
    
    for user in postgresql_users:
        try:
            # Test du login
            login_data = {
                "username": user["email"],  # L'API utilise email comme username
                "password": user["password"]
            }
            
            # Test avec form data pour OAuth2
            response = requests.post(
                f"{api_base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                if access_token:
                    print(f"  ✅ Login réussi: {user['email']} ({user['role']})")
                    tokens[user['email']] = access_token
                    auth_success += 1
                else:
                    print(f"  ❌ Login échoué (pas de token): {user['email']}")
            else:
                print(f"  ❌ Login échoué: {user['email']} - {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"    └─ Détail: {error_detail}")
                except:
                    print(f"    └─ Réponse: {response.text}")
        
        except Exception as e:
            print(f"  ❌ Erreur login {user['email']}: {e}")
    
    print(f"\n[3/4] Test des endpoints protégés avec tokens...")
    
    profile_success = 0
    for user in postgresql_users:
        if user['email'] in tokens:
            try:
                headers = {
                    "Authorization": f"Bearer {tokens[user['email']]}",
                    "Content-Type": "application/json"
                }
                
                # Test du profil utilisateur
                response = requests.get(
                    f"{api_base_url}/users/me",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    profile_data = response.json()
                    print(f"  ✅ Profil récupéré: {user['email']} - {profile_data.get('role', 'unknown')}")
                    profile_success += 1
                else:
                    print(f"  ❌ Profil échoué: {user['email']} - {response.status_code}")
            
            except Exception as e:
                print(f"  ❌ Erreur profil {user['email']}: {e}")
    
    print(f"\n[4/4] Test d'enregistrement d'un nouvel utilisateur...")
    
    try:
        # Test de création d'utilisateur
        new_user_data = {
            "email": "test_postgres@skillforge.ai",
            "username": "test_postgres_user",
            "password": "TestPostgres123!",
            "confirm_password": "TestPostgres123!",
            "first_name": "Test",
            "last_name": "PostgreSQL",
            "terms_accepted": True,
            "privacy_policy_accepted": True
        }
        
        response = requests.post(
            f"{api_base_url}/auth/register",
            json=new_user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            print("  ✅ Nouvel utilisateur créé avec succès")
            register_success = True
        else:
            print(f"  ❌ Enregistrement échoué: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"    └─ Détail: {error_detail}")
            except:
                print(f"    └─ Réponse: {response.text}")
            register_success = False
    
    except Exception as e:
        print(f"  ❌ Erreur enregistrement: {e}")
        register_success = False
    
    print("\n" + "=" * 70)
    print("RÉSULTATS DES TESTS API")
    print("=" * 70)
    print(f"\nAuthentifications réussies: {auth_success}/5")
    print(f"Profils récupérés: {profile_success}/5")
    print(f"Nouvel enregistrement: {'✅' if register_success else '❌'}")
    
    if auth_success >= 3 and profile_success >= 3:
        print("\n🎉 API FONCTIONNELLE - Tests de base réussis!")
        print("\nProchaines étapes:")
        print("  1. Migrer complètement vers PostgreSQL")
        print("  2. Tester tous les endpoints avec PostgreSQL")
        print("  3. Valider la persistance des données")
        return True
    else:
        print("\n❌ TESTS INCOMPLETS - Vérifier la configuration")
        return False

if __name__ == "__main__":
    success = test_postgresql_api()
    sys.exit(0 if success else 1)