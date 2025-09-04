#!/usr/bin/env python3
"""
Script de diagnostic cloud-sql-proxy pour SkillForge AI
Teste la connectivité et fournit des instructions de correction
"""

import asyncio
import socket
import subprocess
import sys
from datetime import datetime

# Configuration pour SkillForge AI
PROJECT_ID = "skillforge-ai-mvp-25"
REGION = "europe-west1" 
INSTANCE_NAME = "skillforge-db"
DATABASE_NAME = "skillforge_db"
USERNAME = "skillforge_user"
PASSWORD = "Psaumes@27"

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 5432

print("DIAGNOSTIC CLOUD-SQL-PROXY - SKILLFORGE AI")
print("=" * 60)
print(f"Configuration:")
print(f"   Project: {PROJECT_ID}")
print(f"   Region: {REGION}")
print(f"   Instance: {INSTANCE_NAME}")
print(f"   Local: {LOCAL_HOST}:{LOCAL_PORT}")
print()

def test_port_listening():
    """Test 1: Verifier si le port 5432 est en ecoute"""
    print("1. Test port 5432 en ecoute...")
    
    try:
        # Creer une socket et essayer de se connecter
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((LOCAL_HOST, LOCAL_PORT))
        sock.close()
        
        if result == 0:
            print("   OK Port 5432 est accessible")
            return True
        else:
            print("   ERREUR Port 5432 n'est pas accessible")
            return False
    except Exception as e:
        print(f"   ERREUR Erreur test port: {e}")
        return False

def test_cloud_sql_proxy_process():
    """Test 2: Verifier si le processus cloud-sql-proxy fonctionne"""
    print("\n2. Test processus cloud-sql-proxy...")
    
    try:
        # Chercher le processus sur Windows
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq cloud_sql_proxy*"],
                capture_output=True,
                text=True
            )
            if "cloud_sql_proxy" in result.stdout:
                print("   OK Processus cloud-sql-proxy detecte")
                return True
            else:
                print("   ERREUR Processus cloud-sql-proxy non trouve")
        else:
            # Linux/Mac
            result = subprocess.run(
                ["pgrep", "-f", "cloud_sql_proxy"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("   OK Processus cloud-sql-proxy detecte")
                return True
            else:
                print("   ERREUR Processus cloud-sql-proxy non trouve")
        
        return False
    except Exception as e:
        print(f"   ERREUR Erreur recherche processus: {e}")
        return False

def test_gcloud_auth():
    """Test 3: Verifier l'authentification gcloud"""
    print("\n3. Test authentification gcloud...")
    
    try:
        # Vérifier gcloud installé
        result = subprocess.run(
            ["gcloud", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("   ERREUR gcloud CLI non installe ou non dans le PATH")
            return False
        
        print("   OK gcloud CLI installe")
        
        # Verifier authentification
        auth_result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if auth_result.stdout.strip():
            active_account = auth_result.stdout.strip()
            print(f"   OK Authentifie avec: {active_account}")
            return True
        else:
            print("   ERREUR Aucun compte gcloud actif")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ERREUR Timeout gcloud (>10s)")
        return False
    except Exception as e:
        print(f"   ERREUR Erreur gcloud: {e}")
        return False

async def test_postgresql_connection():
    """Test 4: Test connexion PostgreSQL directe"""
    print("\n4. Test connexion PostgreSQL...")
    
    try:
        import asyncpg
        
        connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{LOCAL_HOST}:{LOCAL_PORT}/{DATABASE_NAME}"
        
        print(f"   Tentative connexion: postgresql://{USERNAME}:***@{LOCAL_HOST}:{LOCAL_PORT}/{DATABASE_NAME}")
        
        # Tentative de connexion avec timeout
        conn = await asyncio.wait_for(
            asyncpg.connect(connection_string),
            timeout=10.0
        )
        
        # Test requête simple
        result = await conn.fetchval("SELECT current_timestamp")
        await conn.close()
        
        print(f"   OK Connexion PostgreSQL reussie")
        print(f"   Timestamp serveur: {result}")
        return True
        
    except asyncio.TimeoutError:
        print("   ❌ Timeout connexion PostgreSQL (>10s)")
        return False
    except ImportError:
        print("   ❌ Module asyncpg non disponible")
        return False
    except Exception as e:
        print(f"   ❌ Erreur connexion PostgreSQL: {e}")
        return False

def show_cloud_sql_proxy_instructions():
    """Afficher les instructions pour démarrer cloud-sql-proxy"""
    print("\n🚀 INSTRUCTIONS CLOUD-SQL-PROXY")
    print("=" * 60)
    
    print("\n📥 1. Installation (si pas installé):")
    print("   Windows:")
    print("   gcloud components install cloud_sql_proxy")
    print()
    print("   Linux/Mac:")
    print("   wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy")
    print("   chmod +x cloud_sql_proxy")
    
    print("\n🔐 2. Authentification:")
    print("   gcloud auth login")
    print("   gcloud auth application-default login")
    
    print("\n🚀 3. Démarrer cloud-sql-proxy:")
    
    # Commande pour SkillForge AI
    connection_name = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"
    command = f"cloud_sql_proxy -instances={connection_name}=tcp:{LOCAL_PORT}"
    
    print("   Commande complète:")
    print(f"   {command}")
    print()
    print("   Ou avec options avancées:")
    print(f"   cloud_sql_proxy \\")
    print(f"     -instances={connection_name}=tcp:{LOCAL_PORT} \\")
    print(f"     -credential_file=path/to/service-account.json \\")
    print(f"     -log_debug_stdout")
    
    print("\n🔍 4. Vérification:")
    print("   Dans un autre terminal:")
    print(f"   netstat -an | {'findstr' if sys.platform == 'win32' else 'grep'} :{LOCAL_PORT}")
    print()
    print("   Vous devriez voir:")
    print(f"   TCP    127.0.0.1:{LOCAL_PORT}    0.0.0.0:0    LISTENING")

def show_troubleshooting():
    """Guide de dépannage"""
    print("\n🔧 DÉPANNAGE COURANT")
    print("=" * 60)
    
    print("\n❌ Erreur: 'cloud_sql_proxy' is not recognized")
    print("   Solution: Installez gcloud SDK et cloud_sql_proxy")
    print("   https://cloud.google.com/sdk/docs/install")
    
    print("\n❌ Erreur: Permission denied")
    print("   Solution: Authentifiez-vous avec gcloud")
    print("   gcloud auth login")
    
    print("\n❌ Erreur: Connection refused")
    print("   Solutions:")
    print("   1. Vérifiez que le proxy fonctionne")
    print("   2. Vérifiez le nom de l'instance Cloud SQL")
    print("   3. Vérifiez les règles de firewall")
    
    print("\n❌ Erreur: getaddrinfo failed")
    print("   Solutions:")
    print("   1. Vérifiez la connexion internet")
    print("   2. Redémarrez cloud-sql-proxy")
    print("   3. Vérifiez les DNS")

async def main():
    """Fonction principale de diagnostic"""
    start_time = datetime.now()
    
    # Tests séquentiels
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Port
    if test_port_listening():
        tests_passed += 1
    
    # Test 2: Processus
    if test_cloud_sql_proxy_process():
        tests_passed += 1
    
    # Test 3: Auth
    if test_gcloud_auth():
        tests_passed += 1
    
    # Test 4: Connexion DB
    if await test_postgresql_connection():
        tests_passed += 1
    
    # Résultats
    duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("📋 RÉSULTATS DIAGNOSTIC")
    print("=" * 60)
    print(f"⏱️  Durée: {duration:.2f}s")
    print(f"📊 Tests réussis: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 DIAGNOSTIC RÉUSSI!")
        print("✅ cloud-sql-proxy fonctionne correctement")
        print("✅ Vous pouvez lancer la validation complète:")
        print("   python validate_service.py")
        print("   ou")
        print("   .\\run_validation.ps1")
    else:
        print(f"\n❌ DIAGNOSTIC ÉCHOUÉ ({tests_passed}/{total_tests})")
        print("⚠️  cloud-sql-proxy nécessite une configuration")
        
        if tests_passed == 0:
            print("\n🚨 PROBLÈME MAJEUR: cloud-sql-proxy pas configuré")
            show_cloud_sql_proxy_instructions()
        else:
            print("\n🔧 PROBLÈME PARTIEL: ajustements nécessaires")
        
        show_troubleshooting()
    
    return 0 if tests_passed == total_tests else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Diagnostic interrompu")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        sys.exit(1)