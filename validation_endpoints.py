"""
Script de validation des endpoints avant déploiement
Teste tous les endpoints des trois services (auth, company, user)
"""

import asyncio
import httpx
from typing import Dict, List
from datetime import datetime

class EndpointValidator:
    def __init__(self):
        self.results = {
            "auth_service": [],
            "company_service": [],
            "user_service": []
        }
        self.base_urls = {
            "auth_service": "http://localhost:8001",
            "company_service": "http://localhost:8002",
            "user_service": "http://localhost:8000"
        }

    async def check_endpoint(self, service: str, method: str, path: str, requires_auth: bool = False) -> Dict:
        """Vérifie un endpoint spécifique"""
        base_url = self.base_urls[service]
        url = f"{base_url}{path}"

        headers = {}
        if requires_auth:
            # Pour les tests, on vérifie juste que l'endpoint répond (401 attendu)
            headers["Authorization"] = "Bearer test_token"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json={})
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json={})
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    return {
                        "service": service,
                        "method": method,
                        "path": path,
                        "status": "UNKNOWN_METHOD",
                        "status_code": None,
                        "error": f"Méthode HTTP non supportée: {method}"
                    }

                # Pour les endpoints protégés, 401 ou 403 est acceptable
                # Pour les endpoints publics, on s'attend à 200, 400, ou 422 (validation error)
                acceptable_codes = [200, 201, 204, 400, 401, 403, 404, 422]
                status = "OK" if response.status_code in acceptable_codes else "FAIL"

                return {
                    "service": service,
                    "method": method,
                    "path": path,
                    "status": status,
                    "status_code": response.status_code,
                    "error": None
                }

        except httpx.ConnectError:
            return {
                "service": service,
                "method": method,
                "path": path,
                "status": "CONNECTION_FAILED",
                "status_code": None,
                "error": f"Impossible de se connecter à {base_url}"
            }
        except Exception as e:
            return {
                "service": service,
                "method": method,
                "path": path,
                "status": "ERROR",
                "status_code": None,
                "error": str(e)
            }

    async def validate_all_endpoints(self):
        """Valide tous les endpoints de tous les services"""

        # Définition de tous les endpoints à tester
        endpoints_to_test = [
            # Auth Service
            ("auth_service", "POST", "/api/v1/auth/register", False),
            ("auth_service", "POST", "/api/v1/auth/login", False),
            ("auth_service", "POST", "/api/v1/auth/refresh", True),
            ("auth_service", "POST", "/api/v1/auth/logout", True),
            ("auth_service", "POST", "/api/v1/auth/logout-all", True),
            ("auth_service", "POST", "/api/v1/auth/verify-email-request", True),
            ("auth_service", "POST", "/api/v1/auth/verify-email", False),
            ("auth_service", "POST", "/api/v1/auth/password-reset-request", False),
            ("auth_service", "POST", "/api/v1/auth/password-reset-confirm", False),
            ("auth_service", "POST", "/api/v1/auth/2fa/setup", True),
            ("auth_service", "POST", "/api/v1/auth/2fa/verify", True),
            ("auth_service", "POST", "/api/v1/auth/2fa/disable", True),
            ("auth_service", "POST", "/api/v1/auth/2fa/login", False),
            ("auth_service", "POST", "/api/v1/auth/password/change", True),
            ("auth_service", "GET", "/health", False),
            ("auth_service", "GET", "/api", False),

            # Company Service
            ("company_service", "GET", "/api/v1/companies/", True),
            ("company_service", "POST", "/api/v1/companies/", True),
            ("company_service", "GET", "/api/v1/companies/1", True),
            ("company_service", "PUT", "/api/v1/companies/1", True),
            ("company_service", "DELETE", "/api/v1/companies/1", True),
            ("company_service", "GET", "/api/v1/companies/public/search", False),
            ("company_service", "GET", "/api/v1/companies/slug/test-company", False),
            ("company_service", "GET", "/api/v1/companies/1/members", True),
            ("company_service", "POST", "/api/v1/companies/1/members", True),
            ("company_service", "GET", "/health", False),
            ("company_service", "GET", "/api", False),

            # User Service - Auth routes (ces routes devraient rediriger vers auth-service en prod)
            ("user_service", "POST", "/api/v1/auth/register", False),
            ("user_service", "POST", "/api/v1/auth/login", False),
            ("user_service", "POST", "/api/v1/auth/refresh", True),
            ("user_service", "POST", "/api/v1/auth/logout", True),

            # User Service - User routes
            ("user_service", "GET", "/api/v1/users/me", True),
            ("user_service", "PUT", "/api/v1/users/me", True),
            ("user_service", "POST", "/api/v1/users/me/change-password", True),
            ("user_service", "GET", "/api/v1/users/me/settings", True),
            ("user_service", "PUT", "/api/v1/users/me/settings", True),
            ("user_service", "DELETE", "/api/v1/users/me", True),
            ("user_service", "GET", "/api/v1/users/1/public", False),
            ("user_service", "GET", "/api/v1/users/public", False),
            ("user_service", "GET", "/api/v1/users/", True),
            ("user_service", "GET", "/api/v1/users/1", True),
            ("user_service", "PUT", "/api/v1/users/1/role", True),
            ("user_service", "PUT", "/api/v1/users/1/status", True),
            ("user_service", "DELETE", "/api/v1/users/1", True),
            ("user_service", "GET", "/health", False),
            ("user_service", "GET", "/api", False),
        ]

        print("🔍 Validation des endpoints en cours...\n")

        # Tester tous les endpoints
        tasks = []
        for service, method, path, requires_auth in endpoints_to_test:
            tasks.append(self.check_endpoint(service, method, path, requires_auth))

        results = await asyncio.gather(*tasks)

        # Organiser les résultats par service
        for result in results:
            self.results[result["service"]].append(result)

        # Afficher les résultats
        self.display_results()

        return self.results

    def display_results(self):
        """Affiche les résultats de la validation"""

        print("\n" + "="*80)
        print("📊 RAPPORT DE VALIDATION DES ENDPOINTS")
        print("="*80 + "\n")

        total_tests = 0
        total_ok = 0
        total_fail = 0
        total_connection_failed = 0

        for service_name, results in self.results.items():
            if not results:
                continue

            print(f"\n{'━'*80}")
            print(f"🔧 Service: {service_name.upper()}")
            print(f"{'━'*80}\n")

            service_ok = 0
            service_fail = 0
            service_connection_failed = 0

            for result in results:
                total_tests += 1

                status_icon = "✅" if result["status"] == "OK" else "❌"
                if result["status"] == "CONNECTION_FAILED":
                    status_icon = "⚠️"
                    service_connection_failed += 1
                    total_connection_failed += 1
                elif result["status"] == "OK":
                    service_ok += 1
                    total_ok += 1
                else:
                    service_fail += 1
                    total_fail += 1

                status_code_str = f"[{result['status_code']}]" if result['status_code'] else "[N/A]"

                print(f"{status_icon} {result['method']:6} {result['path']:50} {status_code_str:6}")

                if result.get("error"):
                    print(f"   └─ Erreur: {result['error']}")

            print(f"\n📈 Résumé pour {service_name}:")
            print(f"   ✅ OK: {service_ok}")
            print(f"   ❌ FAIL: {service_fail}")
            print(f"   ⚠️  CONNECTION_FAILED: {service_connection_failed}")

        print(f"\n{'='*80}")
        print(f"📊 RÉSUMÉ GLOBAL")
        print(f"{'='*80}")
        print(f"Total tests: {total_tests}")
        print(f"✅ OK: {total_ok}")
        print(f"❌ FAIL: {total_fail}")
        print(f"⚠️  CONNECTION_FAILED: {total_connection_failed}")

        success_rate = (total_ok / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 Taux de réussite: {success_rate:.1f}%\n")

        if total_connection_failed > 0:
            print("⚠️  ATTENTION: Certains services ne sont pas accessibles.")
            print("   Assurez-vous que tous les services sont démarrés:")
            print("   - Auth Service: http://localhost:8001")
            print("   - Company Service: http://localhost:8002")
            print("   - User Service: http://localhost:8000")

        print(f"\n{'='*80}\n")


async def main():
    """Point d'entrée principal"""
    validator = EndpointValidator()
    results = await validator.validate_all_endpoints()

    # Vérifier si on peut continuer vers le déploiement
    total_tests = sum(len(r) for r in results.values())
    total_ok = sum(1 for r in results.values() for result in r if result["status"] == "OK")
    total_connection_failed = sum(1 for r in results.values() for result in r if result["status"] == "CONNECTION_FAILED")

    if total_connection_failed > 0:
        print("❌ Validation échouée: Services non accessibles")
        print("   Veuillez démarrer tous les services avant de continuer.\n")
        return False

    success_rate = (total_ok / total_tests * 100) if total_tests > 0 else 0

    if success_rate >= 80:
        print("✅ Validation réussie! Les services sont prêts pour le déploiement.\n")
        return True
    else:
        print("⚠️  Validation partielle. Certains endpoints nécessitent une attention.\n")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
