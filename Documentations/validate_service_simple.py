#!/usr/bin/env python3
"""
Script de validation simplifié du User-Service SkillForge AI
Version allégée sans dépendances lourdes pour diagnostic rapide
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

# Configuration
# Updated instance name - using skillforge-pg-instance-staging
DATABASE_URL = "postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
ASYNCPG_URL = "postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
API_BASE_URL = "http://127.0.0.1:8000"
SERVICE_PATH = Path(__file__).parent

print("VALIDATION SIMPLIFIEE USER-SERVICE SKILLFORGE AI")
print("=" * 60)

async def test_postgresql_simple():
    """Test 1: Connexion PostgreSQL simple"""
    print("\n1. Test connexion PostgreSQL...")
    
    try:
        # Essayer d'importer asyncpg
        import asyncpg
        
        # Test connexion simple avec paramètres séparés (évite le bug Windows avec @ dans l'URL)
        start_time = time.time()
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="skillforge_user",
            password="Psaumes@27",
            database="skillforge_db"
        )
        
        # Test requête simple
        result = await conn.fetchval("SELECT version()")
        db_name = await conn.fetchval("SELECT current_database()")
        user_name = await conn.fetchval("SELECT current_user")
        
        await conn.close()
        duration = time.time() - start_time
        
        print(f"   OK Connexion reussie ({duration:.2f}s)")
        print(f"   Base: {db_name}")
        print(f"   Utilisateur: {user_name}")
        print(f"   Version: {result.split(',')[0] if result else 'Unknown'}")
        
        return True, f"Connexion réussie en {duration:.2f}s"
        
    except ImportError:
        print("   ERREUR Module asyncpg non disponible")
        return False, "Module asyncpg manquant - installez avec: pip install asyncpg"
    except Exception as e:
        print(f"   ERREUR Erreur connexion: {e}")
        return False, str(e)

def test_files_structure():
    """Test 2: Structure des fichiers"""
    print("\n2. Test structure des fichiers...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "alembic.ini",
        "app/__init__.py",
        "app/models/__init__.py",
        "app/api/__init__.py",
        "app/core/__init__.py"
    ]
    
    missing_files = []
    present_files = []
    
    for file_path in required_files:
        full_path = SERVICE_PATH / file_path
        if full_path.exists():
            present_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} manquant")
    
    success = len(missing_files) == 0
    status = f"{len(present_files)}/{len(required_files)} fichiers présents"
    
    if success:
        print("   ✅ Structure complète")
    else:
        print(f"   ⚠️  Fichiers manquants: {missing_files}")
    
    return success, status

def test_python_imports():
    """Test 3: Imports Python critiques"""
    print("\n3. Test imports Python...")
    
    critical_modules = [
        ("fastapi", "Framework API"),
        ("uvicorn", "Serveur ASGI"), 
        ("asyncpg", "Driver PostgreSQL"),
        ("alembic", "Migrations DB"),
        ("pytest", "Tests unitaires")
    ]
    
    available_modules = []
    missing_modules = []
    
    for module_name, description in critical_modules:
        try:
            __import__(module_name)
            available_modules.append(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError:
            missing_modules.append(module_name)
            print(f"   ❌ {module_name} - {description} (manquant)")
    
    success = len(missing_modules) == 0
    status = f"{len(available_modules)}/{len(critical_modules)} modules disponibles"
    
    if not success:
        print(f"\n   💡 Modules manquants: {', '.join(missing_modules)}")
        print("   💡 Installez avec: pip install " + " ".join(missing_modules))
    
    return success, status

def test_alembic_config():
    """Test 4: Configuration Alembic"""
    print("\n4. Test configuration Alembic...")
    
    try:
        alembic_ini = SERVICE_PATH / "alembic.ini"
        if not alembic_ini.exists():
            print("   ❌ alembic.ini non trouvé")
            return False, "Fichier alembic.ini manquant"
        
        # Lire la configuration
        with open(alembic_ini, 'r') as f:
            config_content = f.read()
        
        if "sqlalchemy.url" in config_content:
            print("   ✅ Configuration Alembic présente")
        else:
            print("   ⚠️  Configuration Alembic incomplète")
        
        # Vérifier le dossier migrations
        migrations_dir = SERVICE_PATH / "alembic"
        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob("versions/*.py"))
            print(f"   📊 {len(migration_files)} fichiers de migration trouvés")
        else:
            print("   ⚠️  Dossier alembic/ manquant")
        
        return True, "Configuration Alembic OK"
        
    except Exception as e:
        print(f"   ❌ Erreur configuration Alembic: {e}")
        return False, str(e)

def test_basic_server():
    """Test 5: Test serveur basique (import seulement)"""
    print("\n5. Test configuration serveur...")
    
    try:
        # Test import du main module
        if (SERVICE_PATH / "main.py").exists():
            print("   ✅ main.py présent")
        else:
            print("   ❌ main.py manquant")
            return False, "main.py manquant"
        
        # Vérifier le port 8000 n'est pas utilisé
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', 8000))
            if result == 0:
                print("   ⚠️  Port 8000 déjà utilisé")
            else:
                print("   ✅ Port 8000 libre")
        
        return True, "Configuration serveur OK"
        
    except Exception as e:
        print(f"   ❌ Erreur test serveur: {e}")
        return False, str(e)

async def main():
    """Fonction principale"""
    start_time = time.time()
    
    print(f"📂 Service Path: {SERVICE_PATH}")
    print(f"🔗 Database: {DATABASE_URL.replace('Psaumes@27', '***')}")
    print()
    
    # Changer vers le répertoire du service
    os.chdir(SERVICE_PATH)
    
    # Tests séquentiels
    tests = [
        ("Connexion PostgreSQL", test_postgresql_simple()),
        ("Structure fichiers", test_files_structure()),
        ("Imports Python", test_python_imports()),
        ("Configuration Alembic", test_alembic_config()),
        ("Configuration serveur", test_basic_server())
    ]
    
    results = {}
    passed_tests = 0
    total_tests = len(tests)
    
    # Exécuter les tests
    for test_name, test_func in tests:
        if asyncio.iscoroutine(test_func):
            success, message = await test_func
        else:
            success, message = test_func
        
        results[test_name] = {
            "success": success,
            "message": message
        }
        
        if success:
            passed_tests += 1
    
    # Résumé final
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 60)
    
    print(f"⏱️  Durée totale: {duration:.2f}s")
    print(f"📊 Tests: {passed_tests}/{total_tests} réussis")
    
    # Afficher les résultats détaillés
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name}: {result['message']}")
    
    if passed_tests == total_tests:
        print("\n🎉 VALIDATION BASIQUE RÉUSSIE!")
        print("✅ Les prérequis de base sont satisfaits")
        print("\n📋 Prochaines étapes:")
        print("1. Installez les dépendances manquantes si nécessaire")
        print("2. Lancez la validation complète: python validate_service.py")
        print("3. Ou utilisez le script PowerShell: .\\run_validation.ps1")
        return 0
    else:
        print(f"\n❌ VALIDATION BASIQUE ÉCHOUÉE!")
        print(f"⚠️  {total_tests - passed_tests} problèmes à corriger")
        print("\n🔧 Actions recommandées:")
        
        for test_name, result in results.items():
            if not result["success"]:
                print(f"- Corriger: {test_name}")
        
        print("\n💡 Solutions courantes:")
        print("- Installer les dépendances: pip install -r requirements.txt")
        print("- Vérifier cloud-sql-proxy: netstat -an | findstr :5432")
        print("- Créer les fichiers manquants dans la structure")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Erreur critique: {e}")
        traceback.print_exc()
        sys.exit(1)