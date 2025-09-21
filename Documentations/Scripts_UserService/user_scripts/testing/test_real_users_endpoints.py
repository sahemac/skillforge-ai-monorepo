#!/usr/bin/env python3
"""
Test des endpoints avec les utilisateurs réels créés en base
"""

import requests
import json
import sys

def test_endpoints_with_real_users():
    """Test des endpoints avec les utilisateurs créés dans la base de données."""
    
    base_url = "http://localhost:8000"
    
    # Utilisateurs créés dans test_final_auth.py
    test_users = [
        {
            "email": "admin@skillforge.ai",
            "password": "AdminPass123!",
            "role": "ADMIN",
            "description": "Platform Administrator"
        },
        {
            "email": "company@techcorp.ai", 
            "password": "CompanyPass123!",
            "role": "COMPANY_CONTACT",
            "description": "Company Contact"
        },
        {
            "email": "student@skillforge.ai",
            "password": "StudentPass123!",
            "role": "USER", 
            "description": "Regular Student"
        }
    ]
    
    print("=" * 70)
    print("TEST DES ENDPOINTS AVEC LES UTILISATEURS RÉELS")
    print("=" * 70)
    
    for user in test_users:
        print(f"\n🔍 Test pour {user['description']} ({user['email']})")
        print("-" * 50)
        
        # Test de connexion
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                
                print(f"✅ LOGIN RÉUSSI")
                print(f"   - Token reçu: {access_token[:50]}...")
                print(f"   - Type: {token_data.get('token_type')}")
                print(f"   - Expire dans: {token_data.get('expires_in')}s")
                
                # Test du profil utilisateur avec le token
                headers = {"Authorization": f"Bearer {access_token}"}
                profile_response = requests.get(f"{base_url}/api/v1/users/me", headers=headers)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"✅ PROFIL RÉCUPÉRÉ")
                    print(f"   - Email: {profile_data.get('email')}")
                    print(f"   - Rôle: {profile_data.get('role')}")
                    print(f"   - Statut: {profile_data.get('status')}")
                    print(f"   - Vérifié: {profile_data.get('is_verified')}")
                    print(f"   - Nom complet: {profile_data.get('full_name')}")
                    
                    # Vérification du rôle attendu
                    expected_role = user["role"].lower()
                    actual_role = profile_data.get('role')
                    if actual_role == expected_role:
                        print(f"✅ RÔLE CORRECT: {actual_role}")
                    else:
                        print(f"❌ RÔLE INCORRECT: attendu {expected_role}, reçu {actual_role}")
                else:
                    print(f"❌ ÉCHEC RÉCUPÉRATION PROFIL: {profile_response.status_code}")
                    print(f"   Response: {profile_response.text}")
                    
            else:
                print(f"❌ ÉCHEC LOGIN: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
    
    print("\n" + "=" * 70)
    print("TEST TERMINÉ")
    print("=" * 70)

if __name__ == "__main__":
    test_endpoints_with_real_users()