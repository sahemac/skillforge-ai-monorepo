#!/usr/bin/env python3
"""
Script de test pour simuler les headers IAP et diagnostiquer
les problèmes d'authentification après OAuth.

Ce script aide à identifier pourquoi le user-service rejette
les requêtes authentifiées par Google OAuth.
"""

import requests
import json
import base64
import time
from typing import Dict, Any

def create_mock_iap_jwt() -> str:
    """
    Crée un JWT IAP simulé (non valide cryptographiquement) 
    pour tester la logique du middleware.
    """
    # Header JWT simulé
    header = {
        "alg": "ES256",
        "typ": "JWT",
        "kid": "test-key-id"
    }
    
    # Payload JWT simulé avec des claims IAP typiques
    payload = {
        "iss": "https://cloud.google.com/iap",
        "aud": "/projects/584748485117/global/backendServices/user-service-backend-staging",
        "email": "test.user@emacsah.com",
        "sub": "accounts.google.com:123456789",
        "exp": int(time.time()) + 3600,  # Expire dans 1 heure
        "iat": int(time.time()),
        "given_name": "Test",
        "family_name": "User",
        "name": "Test User"
    }
    
    # Encodage Base64URL (sans padding pour simuler un vrai JWT)
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    signature_b64 = "fake_signature_for_testing"
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def test_endpoints_without_iap(base_url: str) -> Dict[str, Any]:
    """Test les endpoints sans headers IAP."""
    print("Test des endpoints SANS headers IAP...")
    
    results = {}
    endpoints = [
        "/",
        "/health", 
        "/api/v1/auth/health",
        "/api/v1/docs",
        "/api/v1/auth/login"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            results[endpoint] = {
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "content_length": len(response.content)
            }
            print(f"  OK {endpoint}: {response.status_code}")
        except Exception as e:
            results[endpoint] = {"error": str(e)}
            print(f"  ERROR {endpoint}: {str(e)}")
    
    return results

def test_endpoints_with_mock_iap(base_url: str) -> Dict[str, Any]:
    """Test les endpoints avec headers IAP simulés."""
    print("Test des endpoints AVEC headers IAP simulés...")
    
    mock_jwt = create_mock_iap_jwt()
    headers = {
        "x-goog-iap-jwt-assertion": mock_jwt,
        "x-goog-authenticated-user-id": "accounts.google.com:123456789",
        "x-goog-authenticated-user-email": "test.user@emacsah.com"
    }
    
    results = {}
    endpoints = [
        "/",
        "/health",
        "/api/v1/auth/health", 
        "/api/v1/docs"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)
            results[endpoint] = {
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "headers_sent": dict(headers),
                "response_headers": dict(response.headers)
            }
            print(f"  OK {endpoint}: {response.status_code}")
        except Exception as e:
            results[endpoint] = {"error": str(e)}
            print(f"  ERROR {endpoint}: {str(e)}")
    
    return results

def test_auth_endpoint_with_data(base_url: str) -> Dict[str, Any]:
    """Test spécifique de l'endpoint de login avec des données."""
    print(" Test de l'endpoint /api/v1/auth/login avec données...")
    
    # Test sans IAP headers
    login_data = {
        "email": "test@test.com",
        "password": "testpassword"
    }
    
    results = {}
    
    try:
        url = f"{base_url}/api/v1/auth/login"
        response = requests.post(url, json=login_data, timeout=10)
        results["without_iap"] = {
            "status_code": response.status_code,
            "response_text": response.text[:500],  # Premiers 500 caractères
            "content_type": response.headers.get("content-type")
        }
        print(f"  OK Login sans IAP: {response.status_code}")
    except Exception as e:
        results["without_iap"] = {"error": str(e)}
        print(f"  ERROR Login sans IAP: {str(e)}")
    
    # Test avec IAP headers
    try:
        mock_jwt = create_mock_iap_jwt()
        headers = {
            "x-goog-iap-jwt-assertion": mock_jwt,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=login_data, headers=headers, timeout=10)
        results["with_iap"] = {
            "status_code": response.status_code,
            "response_text": response.text[:500],
            "content_type": response.headers.get("content-type")
        }
        print(f"  OK Login avec IAP: {response.status_code}")
    except Exception as e:
        results["with_iap"] = {"error": str(e)}
        print(f"  ERROR Login avec IAP: {str(e)}")
    
    return results

def analyze_middleware_behavior(results: Dict[str, Any]) -> None:
    """Analyse les résultats pour identifier les problèmes du middleware."""
    print("\n ANALYSE DU COMPORTEMENT DU MIDDLEWARE IAP")
    print("=" * 60)
    
    # Analyse des endpoints sans IAP
    print("\n Endpoints sans headers IAP:")
    for endpoint, result in results["without_iap"].items():
        if "error" in result:
            print(f"  ERROR {endpoint}: ERREUR - {result['error']}")
        elif result["status_code"] >= 400:
            print(f"  WARNING  {endpoint}: HTTP {result['status_code']} (potentiel problème)")
        else:
            print(f"  OK {endpoint}: HTTP {result['status_code']} (OK)")
    
    # Analyse des endpoints avec IAP simulé
    print("\n Endpoints avec headers IAP simulés:")
    for endpoint, result in results["with_iap"].items():
        if "error" in result:
            print(f"  ERROR {endpoint}: ERREUR - {result['error']}")
        elif result["status_code"] >= 400:
            print(f"  WARNING  {endpoint}: HTTP {result['status_code']} (rejet par middleware)")
        else:
            print(f"  OK {endpoint}: HTTP {result['status_code']} (OK)")
    
    # Recommandations
    print("\n RECOMMANDATIONS:")
    
    # Vérifier si le middleware rejette tous les tokens simulés
    iap_rejections = sum(1 for r in results["with_iap"].values() 
                        if not r.get("error") and r["status_code"] >= 400)
    
    if iap_rejections > 0:
        print("  1. Le middleware IAP rejette les tokens simulés")
        print("     → Vérifier la validation JWT dans iap_middleware.py")
        print("     → Problème potentiel: validation des clés publiques Google")
    
    # Vérifier les endpoints sans IAP
    no_iap_rejections = sum(1 for r in results["without_iap"].values() 
                           if not r.get("error") and r["status_code"] >= 400)
    
    if no_iap_rejections > 0:
        print("  2. Certains endpoints rejettent même sans IAP")
        print("     → Problème potentiel dans la logique de l'application")
    
    # Analyse spécifique du login
    if "auth_login" in results:
        login_results = results["auth_login"]
        print(f"  3. Endpoint login:")
        if "without_iap" in login_results:
            status = login_results["without_iap"].get("status_code", "ERROR")
            print(f"     Sans IAP: HTTP {status}")
        if "with_iap" in login_results:
            status = login_results["with_iap"].get("status_code", "ERROR")
            print(f"     Avec IAP: HTTP {status}")

def main():
    """Fonction principale de test."""
    print("DIAGNOSTIC MIDDLEWARE IAP - USER SERVICE")
    print("=" * 60)
    print("Ce script teste le comportement du middleware IAP")
    print("pour identifier pourquoi les requêtes sont rejetées après OAuth.\n")
    
    # URL de base du service (local pour tests)
    base_url = "http://127.0.0.1:8010"
    
    results = {}
    
    # Test 1: Endpoints sans IAP
    results["without_iap"] = test_endpoints_without_iap(base_url)
    
    # Test 2: Endpoints avec IAP simulé  
    results["with_iap"] = test_endpoints_with_mock_iap(base_url)
    
    # Test 3: Endpoint de login spécifique
    results["auth_login"] = test_auth_endpoint_with_data(base_url)
    
    # Analyse des résultats
    analyze_middleware_behavior(results)
    
    # Sauvegarde des résultats
    print(f"\nSauvegarde des résultats dans 'iap_diagnostic_results.json'")
    with open("iap_diagnostic_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nDiagnostic terminé!")
    print("\nProchaines étapes recommandées:")
    print("1. Examiner les logs du service pendant l'exécution de ce script")
    print("2. Vérifier la configuration IAP dans main.py")
    print("3. Tester avec de vrais headers IAP depuis l'environnement production")

if __name__ == "__main__":
    main()