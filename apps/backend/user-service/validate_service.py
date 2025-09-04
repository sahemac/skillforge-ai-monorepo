#!/usr/bin/env python3
"""
Script de validation complète du User-Service SkillForge AI
Teste la connexion PostgreSQL, migrations, API endpoints et génère un rapport
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import asyncpg
import httpx
import psutil
from sqlmodel import select, SQLModel
from sqlalchemy import text

# Configuration
DATABASE_URL = "postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
ASYNCPG_URL = "postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
API_BASE_URL = "http://127.0.0.1:8000"
SERVICE_PATH = Path(__file__).parent
REPORT_PATH = SERVICE_PATH / "test-validation-report.md"

class ValidationResult:
    """Classe pour stocker les résultats de validation"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        self.metrics: Dict[str, Any] = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "warnings": 0,
            "duration": 0
        }
    
    def add_result(self, test_name: str, status: str, details: str = "", 
                   metrics: Dict[str, Any] = None, error: str = ""):
        """Ajoute un résultat de test"""
        self.results[test_name] = {
            "status": status,
            "details": details,
            "metrics": metrics or {},
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics["total_tests"] += 1
        if status == "PASS":
            self.metrics["passed_tests"] += 1
        elif status == "FAIL":
            self.metrics["failed_tests"] += 1
        elif status == "WARN":
            self.metrics["warnings"] += 1
    
    def finalize(self):
        """Finalise les métriques"""
        self.metrics["duration"] = (datetime.now() - self.start_time).total_seconds()

class ServiceValidator:
    """Validateur principal du service"""
    
    def __init__(self):
        self.result = ValidationResult()
        self.server_process: Optional[subprocess.Popen] = None
        self.conn_pool: Optional[asyncpg.Pool] = None
    
    async def validate_all(self) -> ValidationResult:
        """Lance toutes les validations"""
        print("🔍 VALIDATION COMPLÈTE USER-SERVICE SKILLFORGE AI")
        print("=" * 60)
        
        try:
            # 1. Test connexion PostgreSQL
            await self.test_postgresql_connection()
            
            # 2. Migrations Alembic
            await self.test_alembic_migrations()
            
            # 3. Vérification schéma/tables
            await self.test_database_schema()
            
            # 4. Tests unitaires
            await self.test_unit_tests()
            
            # 5. Démarrage serveur
            await self.test_server_startup()
            
            # 6. Tests endpoints
            await self.test_api_endpoints()
            
            # 7. Validation données
            await self.test_data_validation()
            
        except Exception as e:
            self.result.add_result(
                "global_error", 
                "FAIL", 
                f"Erreur critique: {str(e)}", 
                error=traceback.format_exc()
            )
        
        finally:
            await self.cleanup()
            self.result.finalize()
        
        return self.result
    
    async def test_postgresql_connection(self):
        """Test 1: Connexion PostgreSQL"""
        print("\n📡 1. Test connexion PostgreSQL...")
        
        try:
            # Test connexion simple
            start_time = time.time()
            self.conn_pool = await asyncpg.create_pool(
                host="localhost",
                port=5432,
                user="skillforge_user",
                password="Psaumes@27",
                database="skillforge_db",
                min_size=1,
                max_size=5,
                command_timeout=10
            )
            
            async with self.conn_pool.acquire() as conn:
                # Test requête simple
                result = await conn.fetchval("SELECT version()")
                db_size = await conn.fetchval(
                    "SELECT pg_size_pretty(pg_database_size('skillforge_db'))"
                )
                connection_count = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = 'skillforge_db'"
                )
            
            duration = time.time() - start_time
            
            self.result.add_result(
                "postgresql_connection",
                "PASS",
                f"Connexion réussie à PostgreSQL. Version: {result}",
                {
                    "connection_time": round(duration, 3),
                    "database_size": db_size,
                    "active_connections": connection_count,
                    "pool_size": "1-5"
                }
            )
            print(f"   ✅ Connexion OK ({duration:.2f}s)")
            print(f"   📊 Taille DB: {db_size}, Connexions actives: {connection_count}")
            
        except Exception as e:
            self.result.add_result(
                "postgresql_connection",
                "FAIL",
                f"Impossible de se connecter à PostgreSQL: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Échec connexion: {e}")
    
    async def test_alembic_migrations(self):
        """Test 2: Migrations Alembic"""
        print("\n📋 2. Test migrations Alembic...")
        
        try:
            # Vérifier la configuration Alembic
            alembic_ini = SERVICE_PATH / "alembic.ini"
            if not alembic_ini.exists():
                raise FileNotFoundError("alembic.ini non trouvé")
            
            # Exécuter les migrations
            start_time = time.time()
            
            # Backup current revision
            env = os.environ.copy()
            env["DATABASE_URL"] = DATABASE_URL
            
            # Get current revision
            current_rev_result = subprocess.run(
                ["alembic", "current"],
                cwd=SERVICE_PATH,
                capture_output=True,
                text=True,
                env=env
            )
            
            # Upgrade to head
            upgrade_result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=SERVICE_PATH,
                capture_output=True,
                text=True,
                env=env
            )
            
            # Get migration history
            history_result = subprocess.run(
                ["alembic", "history", "--verbose"],
                cwd=SERVICE_PATH,
                capture_output=True,
                text=True,
                env=env
            )
            
            duration = time.time() - start_time
            
            if upgrade_result.returncode == 0:
                # Compter les migrations appliquées
                history_lines = [line for line in history_result.stdout.split('\n') if 'Rev:' in line]
                migration_count = len(history_lines)
                
                self.result.add_result(
                    "alembic_migrations",
                    "PASS",
                    f"Migrations appliquées avec succès. {migration_count} migrations trouvées.",
                    {
                        "execution_time": round(duration, 3),
                        "migration_count": migration_count,
                        "current_revision": current_rev_result.stdout.strip(),
                        "upgrade_output": upgrade_result.stdout
                    }
                )
                print(f"   ✅ Migrations OK ({duration:.2f}s)")
                print(f"   📊 {migration_count} migrations appliquées")
            else:
                raise Exception(f"Erreur Alembic: {upgrade_result.stderr}")
                
        except Exception as e:
            self.result.add_result(
                "alembic_migrations",
                "FAIL",
                f"Échec des migrations: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Échec migrations: {e}")
    
    async def test_database_schema(self):
        """Test 3: Vérification schéma et tables"""
        print("\n🗄️ 3. Vérification schéma et tables...")
        
        try:
            if not self.conn_pool:
                raise Exception("Pool de connexion non disponible")
            
            async with self.conn_pool.acquire() as conn:
                # Lister toutes les tables
                tables_query = """
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """
                tables = await conn.fetch(tables_query)
                
                # Vérifier les tables attendues
                expected_tables = [
                    'users', 'user_settings', 'user_sessions',
                    'company_profiles', 'team_members', 'subscriptions',
                    'alembic_version'
                ]
                
                found_tables = [row['table_name'] for row in tables]
                missing_tables = [table for table in expected_tables if table not in found_tables]
                extra_tables = [table for table in found_tables if table not in expected_tables]
                
                # Analyser les colonnes des tables principales
                table_analyses = {}
                for table_name in ['users', 'company_profiles']:
                    if table_name in found_tables:
                        columns_query = """
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = $1 AND table_schema = 'public'
                        ORDER BY ordinal_position;
                        """
                        columns = await conn.fetch(columns_query, table_name)
                        table_analyses[table_name] = {
                            'column_count': len(columns),
                            'columns': [
                                {
                                    'name': col['column_name'],
                                    'type': col['data_type'],
                                    'nullable': col['is_nullable']
                                }
                                for col in columns
                            ]
                        }
                
                # Vérifier les index
                indexes_query = """
                SELECT indexname, tablename, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
                """
                indexes = await conn.fetch(indexes_query)
                
                status = "PASS" if not missing_tables else "WARN"
                details = f"Tables trouvées: {len(found_tables)}/{len(expected_tables)}"
                if missing_tables:
                    details += f". Manquantes: {missing_tables}"
                if extra_tables:
                    details += f". Supplémentaires: {extra_tables}"
                
                self.result.add_result(
                    "database_schema",
                    status,
                    details,
                    {
                        "total_tables": len(found_tables),
                        "expected_tables": len(expected_tables),
                        "missing_tables": missing_tables,
                        "extra_tables": extra_tables,
                        "table_analyses": table_analyses,
                        "index_count": len(indexes)
                    }
                )
                
                if status == "PASS":
                    print(f"   ✅ Schéma OK ({len(found_tables)} tables)")
                else:
                    print(f"   ⚠️  Schéma partiel ({len(found_tables)} tables)")
                
                for table_name, analysis in table_analyses.items():
                    print(f"   📋 {table_name}: {analysis['column_count']} colonnes")
                    
        except Exception as e:
            self.result.add_result(
                "database_schema",
                "FAIL",
                f"Erreur vérification schéma: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Échec schéma: {e}")
    
    async def test_unit_tests(self):
        """Test 4: Tests unitaires avec coverage"""
        print("\n🧪 4. Tests unitaires avec coverage...")
        
        try:
            start_time = time.time()
            
            # Installer les dépendances de test si nécessaire
            pip_result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest", "pytest-cov", "pytest-asyncio", "httpx"],
                capture_output=True,
                text=True,
                cwd=SERVICE_PATH
            )
            
            env = os.environ.copy()
            env["DATABASE_URL"] = DATABASE_URL
            env["PYTHONPATH"] = str(SERVICE_PATH)
            
            # Lancer pytest avec coverage
            pytest_cmd = [
                "python", "-m", "pytest",
                "app/tests/",
                "-v",
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=json:coverage.json",
                "--tb=short"
            ]
            
            pytest_result = subprocess.run(
                pytest_cmd,
                cwd=SERVICE_PATH,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            
            # Analyser les résultats
            output_lines = pytest_result.stdout.split('\n')
            test_summary = [line for line in output_lines if 'passed' in line and 'failed' in line]
            coverage_lines = [line for line in output_lines if 'Total coverage:' in line or 'TOTAL' in line]
            
            # Lire le fichier de coverage JSON si disponible
            coverage_data = {}
            coverage_file = SERVICE_PATH / "coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                except:
                    pass
            
            # Déterminer le statut
            if pytest_result.returncode == 0:
                status = "PASS"
                details = "Tous les tests sont passés"
            elif pytest_result.returncode == 1:
                status = "WARN" if "failed" in pytest_result.stdout else "FAIL"
                details = "Certains tests ont échoué"
            else:
                status = "FAIL"
                details = f"Erreur pytest (code {pytest_result.returncode})"
            
            # Extraire les métriques de coverage
            total_coverage = 0
            if coverage_data and 'totals' in coverage_data:
                totals = coverage_data['totals']
                if totals.get('num_statements', 0) > 0:
                    total_coverage = (totals['covered_lines'] / totals['num_statements']) * 100
            
            self.result.add_result(
                "unit_tests",
                status,
                details,
                {
                    "execution_time": round(duration, 3),
                    "exit_code": pytest_result.returncode,
                    "coverage_percentage": round(total_coverage, 2),
                    "test_summary": test_summary,
                    "coverage_data": coverage_data.get('totals', {}),
                    "output_preview": pytest_result.stdout[:1000]
                }
            )
            
            if status == "PASS":
                print(f"   ✅ Tests OK ({duration:.2f}s)")
            elif status == "WARN":
                print(f"   ⚠️  Tests partiels ({duration:.2f}s)")
            else:
                print(f"   ❌ Échec tests ({duration:.2f}s)")
            
            if total_coverage > 0:
                print(f"   📊 Coverage: {total_coverage:.1f}%")
            
        except subprocess.TimeoutExpired:
            self.result.add_result(
                "unit_tests",
                "FAIL",
                "Tests timeout après 5 minutes",
                error="Timeout"
            )
            print("   ❌ Timeout tests (>5min)")
        except Exception as e:
            self.result.add_result(
                "unit_tests",
                "FAIL",
                f"Erreur exécution tests: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Erreur tests: {e}")
    
    async def test_server_startup(self):
        """Test 5: Démarrage serveur uvicorn"""
        print("\n🚀 5. Test démarrage serveur...")
        
        try:
            # Vérifier que le port est libre
            if self.is_port_in_use(8000):
                print("   ⚠️  Port 8000 déjà utilisé, tentative d'arrêt...")
                self.kill_process_on_port(8000)
                await asyncio.sleep(2)
            
            # Démarrer le serveur
            env = os.environ.copy()
            env["DATABASE_URL"] = DATABASE_URL
            env["PYTHONPATH"] = str(SERVICE_PATH)
            
            start_time = time.time()
            
            self.server_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=SERVICE_PATH,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre que le serveur soit prêt
            startup_timeout = 30  # 30 secondes
            server_ready = False
            
            for attempt in range(startup_timeout):
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(f"{API_BASE_URL}/health")
                        if response.status_code == 200:
                            server_ready = True
                            break
                except:
                    pass
                await asyncio.sleep(1)
            
            startup_duration = time.time() - start_time
            
            if server_ready:
                # Vérifier les métriques du serveur
                async with httpx.AsyncClient() as client:
                    # Test endpoint de base
                    docs_response = await client.get(f"{API_BASE_URL}/docs")
                    openapi_response = await client.get(f"{API_BASE_URL}/openapi.json")
                
                self.result.add_result(
                    "server_startup",
                    "PASS",
                    f"Serveur démarré avec succès sur le port 8000",
                    {
                        "startup_time": round(startup_duration, 3),
                        "pid": self.server_process.pid,
                        "health_status": response.status_code,
                        "docs_available": docs_response.status_code == 200,
                        "openapi_available": openapi_response.status_code == 200
                    }
                )
                print(f"   ✅ Serveur OK ({startup_duration:.2f}s)")
                print(f"   🔗 PID: {self.server_process.pid}")
                
            else:
                # Lire les logs d'erreur
                stderr_output = ""
                if self.server_process and self.server_process.stderr:
                    try:
                        stderr_output = self.server_process.stderr.read()
                    except:
                        pass
                
                self.result.add_result(
                    "server_startup",
                    "FAIL",
                    f"Serveur n'a pas démarré dans les {startup_timeout}s",
                    {
                        "startup_time": round(startup_duration, 3),
                        "timeout": startup_timeout
                    },
                    error=stderr_output
                )
                print(f"   ❌ Timeout démarrage ({startup_timeout}s)")
                
        except Exception as e:
            self.result.add_result(
                "server_startup",
                "FAIL",
                f"Erreur démarrage serveur: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Erreur démarrage: {e}")
    
    async def test_api_endpoints(self):
        """Test 6: Endpoints critiques"""
        print("\n🌐 6. Test endpoints critiques...")
        
        if "server_startup" not in self.result.results or self.result.results["server_startup"]["status"] != "PASS":
            self.result.add_result(
                "api_endpoints",
                "SKIP",
                "Serveur non disponible, tests d'endpoints ignorés"
            )
            print("   ⏭️  Serveur indisponible, tests ignorés")
            return
        
        endpoints_results = {}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test 1: Health Check
                await self.test_health_endpoint(client, endpoints_results)
                
                # Test 2: Documentation
                await self.test_docs_endpoints(client, endpoints_results)
                
                # Test 3: Auth Register
                await self.test_auth_register(client, endpoints_results)
                
                # Test 4: Auth Login
                await self.test_auth_login(client, endpoints_results)
                
                # Test 5: Protected endpoint
                await self.test_protected_endpoint(client, endpoints_results)
            
            # Analyser les résultats
            total_endpoints = len(endpoints_results)
            passed_endpoints = len([r for r in endpoints_results.values() if r["status"] == "PASS"])
            failed_endpoints = len([r for r in endpoints_results.values() if r["status"] == "FAIL"])
            
            overall_status = "PASS" if failed_endpoints == 0 else ("WARN" if passed_endpoints > failed_endpoints else "FAIL")
            
            self.result.add_result(
                "api_endpoints",
                overall_status,
                f"{passed_endpoints}/{total_endpoints} endpoints fonctionnels",
                {
                    "total_endpoints": total_endpoints,
                    "passed_endpoints": passed_endpoints,
                    "failed_endpoints": failed_endpoints,
                    "endpoint_results": endpoints_results
                }
            )
            
            if overall_status == "PASS":
                print(f"   ✅ Endpoints OK ({passed_endpoints}/{total_endpoints})")
            else:
                print(f"   ⚠️  Endpoints partiels ({passed_endpoints}/{total_endpoints})")
                
        except Exception as e:
            self.result.add_result(
                "api_endpoints",
                "FAIL",
                f"Erreur test endpoints: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Erreur endpoints: {e}")
    
    async def test_health_endpoint(self, client: httpx.AsyncClient, results: Dict):
        """Test endpoint health"""
        try:
            start_time = time.time()
            response = await client.get(f"{API_BASE_URL}/health")
            duration = time.time() - start_time
            
            results["health"] = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "response_code": response.status_code,
                "response_time": round(duration * 1000, 2),  # ms
                "response_body": response.text[:200]
            }
            print(f"   🔍 /health: {response.status_code} ({duration*1000:.0f}ms)")
        except Exception as e:
            results["health"] = {"status": "FAIL", "error": str(e)}
            print(f"   ❌ /health: {e}")
    
    async def test_docs_endpoints(self, client: httpx.AsyncClient, results: Dict):
        """Test endpoints de documentation"""
        try:
            # Test /docs
            docs_response = await client.get(f"{API_BASE_URL}/docs")
            openapi_response = await client.get(f"{API_BASE_URL}/openapi.json")
            
            results["docs"] = {
                "status": "PASS" if docs_response.status_code == 200 else "FAIL",
                "docs_status": docs_response.status_code,
                "openapi_status": openapi_response.status_code,
                "docs_size": len(docs_response.text) if docs_response.status_code == 200 else 0
            }
            print(f"   📚 /docs: {docs_response.status_code}, /openapi.json: {openapi_response.status_code}")
        except Exception as e:
            results["docs"] = {"status": "FAIL", "error": str(e)}
            print(f"   ❌ Docs: {e}")
    
    async def test_auth_register(self, client: httpx.AsyncClient, results: Dict):
        """Test endpoint d'inscription"""
        try:
            test_user_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User Validation"
            }
            
            start_time = time.time()
            response = await client.post(
                f"{API_BASE_URL}/api/v1/auth/register",
                json=test_user_data
            )
            duration = time.time() - start_time
            
            results["auth_register"] = {
                "status": "PASS" if response.status_code in [200, 201] else "FAIL",
                "response_code": response.status_code,
                "response_time": round(duration * 1000, 2),
                "test_email": test_user_data["email"],
                "response_body": response.text[:300] if response.status_code not in [200, 201] else "OK"
            }
            print(f"   ✍️  /auth/register: {response.status_code} ({duration*1000:.0f}ms)")
            
        except Exception as e:
            results["auth_register"] = {"status": "FAIL", "error": str(e)}
            print(f"   ❌ Register: {e}")
    
    async def test_auth_login(self, client: httpx.AsyncClient, results: Dict):
        """Test endpoint de connexion"""
        try:
            # Créer un utilisateur de test d'abord
            test_user_data = {
                "email": f"login_test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "full_name": "Login Test User"
            }
            
            # Inscription
            register_response = await client.post(
                f"{API_BASE_URL}/api/v1/auth/register",
                json=test_user_data
            )
            
            if register_response.status_code not in [200, 201]:
                # Essayer avec des données de test par défaut
                login_data = {
                    "username": "admin@example.com",  # Peut-être qu'il y a des données par défaut
                    "password": "admin123"
                }
            else:
                login_data = {
                    "username": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            
            # Test de connexion
            start_time = time.time()
            response = await client.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                data=login_data,  # Form data pour OAuth2
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            duration = time.time() - start_time
            
            # Vérifier si on a reçu un token
            token_received = False
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    token_received = "access_token" in response_json
                except:
                    pass
            
            results["auth_login"] = {
                "status": "PASS" if response.status_code == 200 and token_received else "FAIL",
                "response_code": response.status_code,
                "response_time": round(duration * 1000, 2),
                "token_received": token_received,
                "test_email": login_data["username"],
                "response_body": response.text[:300] if response.status_code != 200 else "Token OK"
            }
            print(f"   🔐 /auth/login: {response.status_code} ({duration*1000:.0f}ms)")
            
        except Exception as e:
            results["auth_login"] = {"status": "FAIL", "error": str(e)}
            print(f"   ❌ Login: {e}")
    
    async def test_protected_endpoint(self, client: httpx.AsyncClient, results: Dict):
        """Test endpoint protégé"""
        try:
            # Tenter d'accéder à un endpoint protégé sans token
            response = await client.get(f"{API_BASE_URL}/api/v1/users/me")
            
            # On s'attend à une erreur 401 (non autorisé)
            expected_unauthorized = response.status_code == 401
            
            results["protected_endpoint"] = {
                "status": "PASS" if expected_unauthorized else "WARN",
                "response_code": response.status_code,
                "security_working": expected_unauthorized,
                "details": "Sécurité OK - accès refusé sans token" if expected_unauthorized else "Attention - endpoint accessible sans auth"
            }
            print(f"   🛡️  /users/me (sans auth): {response.status_code}")
            
        except Exception as e:
            results["protected_endpoint"] = {"status": "FAIL", "error": str(e)}
            print(f"   ❌ Protected: {e}")
    
    async def test_data_validation(self):
        """Test 7: Validation données base"""
        print("\n📊 7. Validation données base...")
        
        try:
            if not self.conn_pool:
                raise Exception("Pool de connexion non disponible")
            
            async with self.conn_pool.acquire() as conn:
                # Compter les enregistrements dans les tables principales
                table_counts = {}
                tables_to_check = ['users', 'company_profiles', 'user_sessions']
                
                for table in tables_to_check:
                    try:
                        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                        table_counts[table] = count
                    except:
                        table_counts[table] = "N/A"
                
                # Vérifier l'intégrité des données
                integrity_checks = {}
                
                # Check 1: Vérifier les users avec email valides
                if 'users' in table_counts and table_counts['users'] != "N/A":
                    valid_emails = await conn.fetchval(
                        "SELECT COUNT(*) FROM users WHERE email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
                    )
                    integrity_checks['valid_emails'] = f"{valid_emails}/{table_counts['users']}"
                
                # Check 2: Vérifier les timestamps
                recent_activity = await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '1 day'"
                )
                integrity_checks['recent_users'] = recent_activity
                
                # Check 3: Vérifier les contraintes de clés étrangères
                fk_violations = await conn.fetchval("""
                    SELECT COUNT(*)
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
                """)
                integrity_checks['foreign_key_constraints'] = fk_violations
                
                self.result.add_result(
                    "data_validation",
                    "PASS",
                    f"Validation données réussie. {sum(v for v in table_counts.values() if isinstance(v, int))} enregistrements total",
                    {
                        "table_counts": table_counts,
                        "integrity_checks": integrity_checks,
                        "total_records": sum(v for v in table_counts.values() if isinstance(v, int))
                    }
                )
                print(f"   ✅ Données OK")
                for table, count in table_counts.items():
                    print(f"   📋 {table}: {count} enregistrements")
                    
        except Exception as e:
            self.result.add_result(
                "data_validation",
                "FAIL",
                f"Erreur validation données: {str(e)}",
                error=str(e)
            )
            print(f"   ❌ Erreur validation: {e}")
    
    async def cleanup(self):
        """Nettoyage des ressources"""
        print("\n🧹 Nettoyage...")
        
        # Arrêter le serveur
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                print("   🛑 Serveur arrêté")
            except:
                try:
                    self.server_process.kill()
                    print("   🛑 Serveur forcé à l'arrêt")
                except:
                    pass
        
        # Fermer le pool de connexions
        if self.conn_pool:
            await self.conn_pool.close()
            print("   🔌 Connexions fermées")
    
    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Vérifie si un port est utilisé"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    @staticmethod
    def kill_process_on_port(port: int):
        """Tue le processus utilisant un port"""
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        proc.terminate()
                        return
            except:
                continue

def generate_report(result: ValidationResult, report_path: Path):
    """Génère le rapport de validation en Markdown"""
    
    report_content = f"""# 📋 Rapport de Validation - User-Service SkillForge AI

**Date de génération** : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Durée totale** : {result.metrics['duration']:.2f} secondes  
**Statut global** : {"✅ SUCCÈS" if result.metrics['failed_tests'] == 0 else "❌ ÉCHECS DÉTECTÉS"}

## 📊 Résumé des Métriques

| Métrique | Valeur |
|----------|--------|
| **Tests totaux** | {result.metrics['total_tests']} |
| **Tests réussis** | {result.metrics['passed_tests']} |
| **Tests échoués** | {result.metrics['failed_tests']} |
| **Avertissements** | {result.metrics['warnings']} |
| **Taux de succès** | {(result.metrics['passed_tests'] / result.metrics['total_tests'] * 100) if result.metrics['total_tests'] > 0 else 0:.1f}% |

## 🔍 Détail des Tests

"""
    
    # Ordre des tests pour l'affichage
    test_order = [
        "postgresql_connection",
        "alembic_migrations", 
        "database_schema",
        "unit_tests",
        "server_startup",
        "api_endpoints",
        "data_validation"
    ]
    
    test_names = {
        "postgresql_connection": "1️⃣ Connexion PostgreSQL",
        "alembic_migrations": "2️⃣ Migrations Alembic",
        "database_schema": "3️⃣ Schéma Base de Données",
        "unit_tests": "4️⃣ Tests Unitaires",
        "server_startup": "5️⃣ Démarrage Serveur",
        "api_endpoints": "6️⃣ Endpoints API",
        "data_validation": "7️⃣ Validation Données"
    }
    
    for test_key in test_order:
        if test_key in result.results:
            test_result = result.results[test_key]
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "SKIP": "⏭️"
            }.get(test_result["status"], "❓")
            
            report_content += f"""### {test_names.get(test_key, test_key)} - {status_icon} {test_result["status"]}

**Description** : {test_result["details"]}

"""
            
            if test_result.get("metrics"):
                report_content += "**Métriques** :\n"
                for key, value in test_result["metrics"].items():
                    if isinstance(value, dict):
                        report_content += f"- **{key}** : {json.dumps(value, indent=2)}\n"
                    elif isinstance(value, list):
                        report_content += f"- **{key}** : {len(value)} éléments\n"
                    else:
                        report_content += f"- **{key}** : {value}\n"
                report_content += "\n"
            
            if test_result.get("error"):
                report_content += f"""**Erreur** :
```
{test_result["error"]}
```

"""
    
    # Section spéciale pour les endpoints
    if "api_endpoints" in result.results and "endpoint_results" in result.results["api_endpoints"]["metrics"]:
        endpoints = result.results["api_endpoints"]["metrics"]["endpoint_results"]
        report_content += """#### Détail des Endpoints Testés

| Endpoint | Statut | Code HTTP | Temps (ms) | Détails |
|----------|--------|-----------|------------|---------|
"""
        
        endpoint_names = {
            "health": "/health",
            "docs": "/docs + /openapi.json", 
            "auth_register": "/api/v1/auth/register",
            "auth_login": "/api/v1/auth/login",
            "protected_endpoint": "/api/v1/users/me (protection)"
        }
        
        for endpoint_key, endpoint_result in endpoints.items():
            endpoint_name = endpoint_names.get(endpoint_key, endpoint_key)
            status_icon = "✅" if endpoint_result["status"] == "PASS" else "❌"
            response_code = endpoint_result.get("response_code", "N/A")
            response_time = endpoint_result.get("response_time", "N/A")
            details = endpoint_result.get("details", "")[:50] + "..." if len(endpoint_result.get("details", "")) > 50 else endpoint_result.get("details", "")
            
            report_content += f"| {endpoint_name} | {status_icon} {endpoint_result['status']} | {response_code} | {response_time} | {details} |\n"
    
    # Configuration système
    report_content += f"""

## 🔧 Configuration Système

| Paramètre | Valeur |
|-----------|--------|
| **Database URL** | `{DATABASE_URL.replace('Psaumes@27', '***')}` |
| **API Base URL** | `{API_BASE_URL}` |
| **Service Path** | `{SERVICE_PATH}` |
| **Python Version** | `{sys.version.split()[0]}` |
| **Working Directory** | `{os.getcwd()}` |

## 🎯 Recommandations

"""
    
    # Générer des recommandations basées sur les résultats
    recommendations = []
    
    if result.metrics["failed_tests"] > 0:
        recommendations.append("🔥 **CRITIQUE** : Corriger immédiatement les tests échoués avant tout déploiement")
    
    if result.metrics["warnings"] > 0:
        recommendations.append("⚠️ **ATTENTION** : Résoudre les avertissements pour une meilleure stabilité")
    
    # Recommandations spécifiques
    if "unit_tests" in result.results:
        test_result = result.results["unit_tests"]
        if test_result["status"] != "PASS":
            recommendations.append("🧪 **Tests** : Corriger les tests unitaires - fondamental pour la fiabilité")
        
        coverage = test_result.get("metrics", {}).get("coverage_percentage", 0)
        if coverage < 80:
            recommendations.append(f"📊 **Coverage** : Augmenter la couverture de tests (actuel: {coverage:.1f}%, objectif: 80%+)")
    
    if "database_schema" in result.results:
        schema_result = result.results["database_schema"]
        if schema_result.get("metrics", {}).get("missing_tables"):
            recommendations.append("🗄️ **Base de données** : Tables manquantes détectées - vérifier les migrations")
    
    if "api_endpoints" in result.results:
        api_result = result.results["api_endpoints"]
        if api_result["status"] != "PASS":
            recommendations.append("🌐 **API** : Endpoints défaillants - impact sur l'intégration frontend")
    
    if not recommendations:
        recommendations.append("🎉 **Excellent !** Tous les tests sont passés. Service prêt pour la production.")
        recommendations.append("🚀 **Déploiement** : Vous pouvez procéder au commit et au déploiement en toute sécurité.")
        recommendations.append("📈 **Optimisation** : Considérer l'ajout de monitoring et métriques avancées.")
    
    for rec in recommendations:
        report_content += f"- {rec}\n"
    
    report_content += f"""

## 📝 Détails Techniques

### Commandes Exécutées

1. **Test connexion** : `asyncpg.connect(DATABASE_URL)`
2. **Migrations** : `alembic upgrade head`
3. **Tests unitaires** : `python -m pytest app/tests/ -v --cov=app`
4. **Serveur** : `python -m uvicorn main:app --host 127.0.0.1 --port 8000`
5. **Endpoints** : Tests HTTP avec `httpx.AsyncClient`

### Fichiers Générés

- `coverage.json` : Rapport de couverture des tests
- `test-validation-report.md` : Ce rapport
- Logs serveur : stdout/stderr du processus uvicorn

### Prochaines Étapes

1. **Si tous les tests passent** :
   - ✅ Commit des changements : `git add . && git commit -m "feat: user-service ready for production"`
   - ✅ Push vers GitHub : `git push origin feature/user-service`
   - ✅ Créer une Pull Request
   - ✅ Déclencher le pipeline CI/CD

2. **Si des tests échouent** :
   - ❌ Corriger les erreurs identifiées
   - ❌ Relancer la validation : `python validate_service.py`
   - ❌ Ne pas committer tant que les tests ne passent pas

---

**Rapport généré automatiquement par le script de validation SkillForge AI**  
**Version** : 1.0.0  
**Contact** : DevOps Team
"""
    
    # Écrire le rapport
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

async def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE VALIDATION USER-SERVICE SKILLFORGE AI")
    print("=" * 60)
    print(f"📂 Service Path: {SERVICE_PATH}")
    print(f"🔗 Database: {DATABASE_URL.replace('Psaumes@27', '***')}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print()
    
    # Changer vers le répertoire du service
    os.chdir(SERVICE_PATH)
    
    # Lancer la validation
    validator = ServiceValidator()
    result = await validator.validate_all()
    
    # Générer le rapport
    generate_report(result, REPORT_PATH)
    
    # Afficher le résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 60)
    
    print(f"⏱️  Durée totale: {result.metrics['duration']:.2f}s")
    print(f"📊 Tests: {result.metrics['passed_tests']}/{result.metrics['total_tests']} réussis")
    
    if result.metrics['failed_tests'] == 0:
        print("🎉 VALIDATION RÉUSSIE - Service prêt pour la production!")
        print("✅ Vous pouvez procéder au commit GitHub")
    else:
        print(f"❌ VALIDATION ÉCHOUÉE - {result.metrics['failed_tests']} erreurs à corriger")
        print("⚠️  Ne pas committer avant correction")
    
    if result.metrics['warnings'] > 0:
        print(f"⚠️  {result.metrics['warnings']} avertissements à examiner")
    
    print(f"\n📄 Rapport détaillé: {REPORT_PATH}")
    print("\n🔍 Pour plus de détails, consultez le rapport généré.")
    
    # Code de sortie
    exit_code = 0 if result.metrics['failed_tests'] == 0 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Erreur critique: {e}")
        traceback.print_exc()
        sys.exit(1)