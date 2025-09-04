#!/usr/bin/env python3
"""
Script de validation simplifie du User-Service SkillForge AI
Version sans emojis pour compatibilite Windows
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
        
        # Test connexion avec parametres separes (evite bug Windows avec @ dans URL)
        start_time = time.time()
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="skillforge_user",
            password="Psaumes@27",
            database="skillforge_db"
        )
        
        # Test requete simple
        result = await conn.fetchval("SELECT version()")
        db_name = await conn.fetchval("SELECT current_database()")
        user_name = await conn.fetchval("SELECT current_user")
        
        await conn.close()
        duration = time.time() - start_time
        
        print(f"   OK Connexion reussie ({duration:.2f}s)")
        print(f"   Base: {db_name}")
        print(f"   Utilisateur: {user_name}")
        print(f"   Version: {result.split(',')[0] if result else 'Unknown'}")
        
        return True, f"Connexion reussie en {duration:.2f}s"
        
    except ImportError:
        print("   ERREUR Module asyncpg non disponible")
        return False, "Module asyncpg manquant - installez avec: pip install asyncpg"
    except Exception as e:
        print(f"   ERREUR Connexion echouee: {e}")
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
            print(f"   OK {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ERREUR {file_path} manquant")
    
    success = len(missing_files) == 0
    status = f"{len(present_files)}/{len(required_files)} fichiers presents"
    
    if success:
        print("   OK Structure complete")
    else:
        print(f"   ATTENTION Fichiers manquants: {missing_files}")
    
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
            print(f"   OK {module_name} - {description}")
        except ImportError:
            missing_modules.append(module_name)
            print(f"   ERREUR {module_name} - {description} (manquant)")
    
    success = len(missing_modules) == 0
    status = f"{len(available_modules)}/{len(critical_modules)} modules disponibles"
    
    if not success:
        print(f"\n   INFO Modules manquants: {', '.join(missing_modules)}")
        print("   INFO Installez avec: pip install " + " ".join(missing_modules))
    
    return success, status

def test_alembic_config():
    """Test 4: Configuration Alembic"""
    print("\n4. Test configuration Alembic...")
    
    try:
        alembic_ini = SERVICE_PATH / "alembic.ini"
        if not alembic_ini.exists():
            print("   ERREUR alembic.ini non trouve")
            return False, "Fichier alembic.ini manquant"
        
        # Lire la configuration
        with open(alembic_ini, 'r') as f:
            config_content = f.read()
        
        if "sqlalchemy.url" in config_content:
            print("   OK Configuration Alembic presente")
        else:
            print("   ATTENTION Configuration Alembic incomplete")
        
        # Verifier le dossier migrations
        migrations_dir = SERVICE_PATH / "alembic"
        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob("versions/*.py"))
            print(f"   INFO {len(migration_files)} fichiers de migration trouves")
        else:
            print("   ATTENTION Dossier alembic/ manquant")
        
        return True, "Configuration Alembic OK"
        
    except Exception as e:
        print(f"   ERREUR Configuration Alembic: {e}")
        return False, str(e)

def test_basic_server():
    """Test 5: Test serveur basique (import seulement)"""
    print("\n5. Test configuration serveur...")
    
    try:
        # Test import du main module
        if (SERVICE_PATH / "main.py").exists():
            print("   OK main.py present")
        else:
            print("   ERREUR main.py manquant")
            return False, "main.py manquant"
        
        # Verifier le port 8000 n'est pas utilise
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', 8000))
            if result == 0:
                print("   ATTENTION Port 8000 deja utilise")
            else:
                print("   OK Port 8000 libre")
        
        return True, "Configuration serveur OK"
        
    except Exception as e:
        print(f"   ERREUR Test serveur: {e}")
        return False, str(e)

async def main():
    """Fonction principale"""
    start_time = time.time()
    
    print(f"Service Path: {SERVICE_PATH}")
    print(f"Database: {DATABASE_URL.replace('Psaumes@27', '***')}")
    print()
    
    # Changer vers le repertoire du service
    os.chdir(SERVICE_PATH)
    
    # Tests sequentiels
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
    
    # Executer les tests
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
    
    # Resume final
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("RESUME FINAL")
    print("=" * 60)
    
    print(f"Duree totale: {duration:.2f}s")
    print(f"Tests: {passed_tests}/{total_tests} reussis")
    
    # Afficher les resultats detailles
    for test_name, result in results.items():
        status = "PASS" if result["success"] else "FAIL"
        print(f"{status} {test_name}: {result['message']}")
    
    if passed_tests == total_tests:
        print("\nSUCCESS - VALIDATION BASIQUE REUSSIE!")
        print("Les prerequis de base sont satisfaits")
        print("\nProchaines etapes:")
        print("1. Installez les dependances manquantes si necessaire")
        print("2. Lancez la validation complete: python validate_service.py")
        print("3. Ou utilisez le script PowerShell: .\\run_validation.ps1")
        return 0
    else:
        print(f"\nERREUR - VALIDATION BASIQUE ECHOUEE!")
        print(f"ATTENTION: {total_tests - passed_tests} problemes a corriger")
        print("\nActions recommandees:")
        
        for test_name, result in results.items():
            if not result["success"]:
                print(f"- Corriger: {test_name}")
        
        print("\nSolutions courantes:")
        print("- Installer les dependances: pip install -r requirements.txt")
        print("- Verifier cloud-sql-proxy: netstat -an | findstr :5432")
        print("- Creer les fichiers manquants dans la structure")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nERREUR CRITIQUE: {e}")
        traceback.print_exc()
        sys.exit(1)