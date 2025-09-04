#!/usr/bin/env python3
"""
Test rapide de connectivité pour le User-Service SkillForge AI
Vérifie uniquement la connexion PostgreSQL et les dépendances de base
"""

import asyncio
import sys
import time
from pathlib import Path

async def quick_test():
    """Test rapide de connectivité"""
    print("🔍 TEST RAPIDE USER-SERVICE SKILLFORGE AI")
    print("=" * 50)
    
    success = True
    
    # Test 1: Imports Python
    print("\n📦 1. Test des imports Python...")
    try:
        import asyncpg
        import httpx
        import psutil
        from sqlmodel import SQLModel
        print("   ✅ Tous les imports OK")
    except ImportError as e:
        print(f"   ❌ Import manquant: {e}")
        print("   💡 Installez: pip install asyncpg httpx psutil sqlmodel")
        success = False
    
    # Test 2: Connexion PostgreSQL
    print("\n🔗 2. Test connexion PostgreSQL...")
    try:
        DATABASE_URL = "postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
        
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test requête simple
        version = await conn.fetchval("SELECT version()")
        db_name = await conn.fetchval("SELECT current_database()")
        user_name = await conn.fetchval("SELECT current_user")
        
        await conn.close()
        
        print("   ✅ Connexion PostgreSQL OK")
        print(f"   📊 Base: {db_name}")
        print(f"   👤 Utilisateur: {user_name}")
        print(f"   🔧 Version: {version.split(',')[0]}")
        
    except Exception as e:
        print(f"   ❌ Erreur connexion PostgreSQL: {e}")
        print("   💡 Vérifiez que cloud-sql-proxy fonctionne sur 127.0.0.1:5432")
        success = False
    
    # Test 3: Port API libre
    print("\n🌐 3. Test port API (8000)...")
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', 8000))
            if result == 0:
                print("   ⚠️  Port 8000 déjà utilisé")
            else:
                print("   ✅ Port 8000 libre")
    except Exception as e:
        print(f"   ⚠️  Erreur test port: {e}")
    
    # Test 4: Fichiers service
    print("\n📁 4. Test fichiers service...")
    service_files = [
        "main.py",
        "requirements.txt", 
        "alembic.ini",
        "app/__init__.py",
        "app/models/__init__.py",
        "app/api/__init__.py"
    ]
    
    missing_files = []
    for file_path in service_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} manquant")
            missing_files.append(file_path)
    
    if missing_files:
        success = False
        print(f"   💡 Fichiers manquants: {len(missing_files)}")
    
    # Résultat final
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST RAPIDE RÉUSSI!")
        print("✅ Vous pouvez lancer la validation complète avec:")
        print("   python validate_service.py")
        print("   ou")
        print("   .\\run_validation.ps1")
        return 0
    else:
        print("❌ TEST RAPIDE ÉCHOUÉ!")
        print("⚠️  Corrigez les erreurs avant la validation complète")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(quick_test())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Erreur: {e}")
        sys.exit(1)