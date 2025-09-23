#!/usr/bin/env python3
"""
Script de test de connectivité DB pour SkillForge AI
Teste la connectivité depuis les services Cloud Run vers Cloud SQL
"""

import os
import sys
import asyncio
import logging
import time
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseConnectivityTester:
    def __init__(self):
        """Initialise le testeur de connectivité"""
        self.postgres_host = os.getenv('POSTGRES_HOST', '127.0.0.1')
        self.postgres_port = os.getenv('POSTGRES_PORT', '5432')
        self.postgres_db = os.getenv('POSTGRES_DB', 'skillforge_db')
        self.postgres_user = os.getenv('POSTGRES_USER', 'skillforge_user')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD')
        
        if not self.postgres_password:
            logger.error("❌ POSTGRES_PASSWORD n'est pas défini")
            sys.exit(1)
        
        self.database_url = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
        logger.info(f"🔧 Configuration DB:")
        logger.info(f"   Host: {self.postgres_host}")
        logger.info(f"   Port: {self.postgres_port}")
        logger.info(f"   Database: {self.postgres_db}")
        logger.info(f"   User: {self.postgres_user}")
        logger.info(f"   Password: {'*' * len(self.postgres_password)}")

    async def test_basic_connection(self):
        """Test la connexion de base"""
        logger.info("🔌 Test de connexion de base...")
        
        try:
            engine = create_async_engine(self.database_url, echo=False)
            
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                
                if row and row[0] == 1:
                    logger.info("✅ Connexion de base réussie")
                    return True
                else:
                    logger.error("❌ Échec du test de base")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur de connexion: {e}")
            return False
        finally:
            await engine.dispose()

    async def test_database_info(self):
        """Récupère les informations de la base de données"""
        logger.info("📊 Récupération des informations DB...")
        
        try:
            engine = create_async_engine(self.database_url, echo=False)
            
            async with engine.begin() as conn:
                # Version PostgreSQL
                result = await conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"   Version PostgreSQL: {version.split(',')[0]}")
                
                # Nom de la base de données
                result = await conn.execute(text("SELECT current_database()"))
                current_db = result.fetchone()[0]
                logger.info(f"   Base de données courante: {current_db}")
                
                # Utilisateur courant
                result = await conn.execute(text("SELECT current_user"))
                current_user = result.fetchone()[0]
                logger.info(f"   Utilisateur courant: {current_user}")
                
                # Heure du serveur
                result = await conn.execute(text("SELECT NOW()"))
                server_time = result.fetchone()[0]
                logger.info(f"   Heure du serveur: {server_time}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des infos: {e}")
            return False
        finally:
            await engine.dispose()

    async def test_tables_access(self):
        """Teste l'accès aux tables existantes"""
        logger.info("📋 Test d'accès aux tables...")
        
        try:
            engine = create_async_engine(self.database_url, echo=False)
            
            async with engine.begin() as conn:
                # Liste des tables
                result = await conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in result.fetchall()]
                
                if tables:
                    logger.info(f"   Tables trouvées ({len(tables)}):")
                    for table in tables[:10]:  # Afficher max 10 tables
                        logger.info(f"     - {table}")
                    if len(tables) > 10:
                        logger.info(f"     ... et {len(tables) - 10} autres")
                else:
                    logger.warning("   Aucune table trouvée dans le schéma public")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'accès aux tables: {e}")
            return False
        finally:
            await engine.dispose()

    async def test_migrations_table(self):
        """Teste l'accès à la table des migrations Alembic"""
        logger.info("🔄 Test de la table des migrations...")
        
        try:
            engine = create_async_engine(self.database_url, echo=False)
            
            async with engine.begin() as conn:
                # Vérifier la table alembic_version
                result = await conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                """))
                
                table_exists = result.fetchone()[0] > 0
                
                if table_exists:
                    # Récupérer la version courante
                    result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                    version_row = result.fetchone()
                    
                    if version_row:
                        logger.info(f"   Version de migration courante: {version_row[0]}")
                    else:
                        logger.warning("   Table des migrations existe mais aucune version trouvée")
                else:
                    logger.warning("   Table alembic_version n'existe pas")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du test des migrations: {e}")
            return False
        finally:
            await engine.dispose()

    async def test_performance(self):
        """Test de performance simple"""
        logger.info("⚡ Test de performance...")
        
        try:
            engine = create_async_engine(self.database_url, echo=False)
            
            start_time = time.time()
            
            async with engine.begin() as conn:
                # Test simple de requête
                for i in range(10):
                    await conn.execute(text("SELECT 1"))
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # en millisecondes
            
            logger.info(f"   10 requêtes simples en {duration:.2f}ms")
            logger.info(f"   Moyenne: {duration/10:.2f}ms par requête")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du test de performance: {e}")
            return False
        finally:
            await engine.dispose()

    async def run_all_tests(self):
        """Exécute tous les tests"""
        logger.info("🚀 Début des tests de connectivité DB")
        logger.info("=" * 60)
        
        tests = [
            ("Connexion de base", self.test_basic_connection),
            ("Informations DB", self.test_database_info),
            ("Accès aux tables", self.test_tables_access),
            ("Table des migrations", self.test_migrations_table),
            ("Performance", self.test_performance)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name}")
            logger.info("-" * 40)
            
            try:
                success = await test_func()
                results.append((test_name, success))
                
                if success:
                    logger.info(f"✅ {test_name}: SUCCÈS")
                else:
                    logger.error(f"❌ {test_name}: ÉCHEC")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERREUR - {e}")
                results.append((test_name, False))
        
        # Résumé
        logger.info("\n" + "=" * 60)
        logger.info("📊 RÉSUMÉ DES TESTS")
        logger.info("=" * 60)
        
        successful_tests = sum(1 for _, success in results if success)
        total_tests = len(results)
        
        for test_name, success in results:
            status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
            logger.info(f"   {test_name}: {status}")
        
        logger.info("-" * 60)
        logger.info(f"   Total: {successful_tests}/{total_tests} tests réussis")
        
        if successful_tests == total_tests:
            logger.info("🎉 TOUS LES TESTS SONT RÉUSSIS!")
            return True
        else:
            logger.error(f"⚠️  {total_tests - successful_tests} test(s) ont échoué")
            return False

async def main():
    """Fonction principale"""
    logger.info("🔧 Testeur de connectivité DB SkillForge AI")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    tester = DatabaseConnectivityTester()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n✅ Tous les tests de connectivité ont réussi!")
        sys.exit(0)
    else:
        logger.error("\n❌ Certains tests ont échoué. Vérifiez la configuration.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())