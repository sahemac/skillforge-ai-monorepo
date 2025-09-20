#!/usr/bin/env python3
"""
Script de migration automatique pour SkillForge User Service
Supporte les environnements locaux et Cloud SQL avec secrets
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Gestionnaire de migrations automatiques pour la base de données"""
    
    def __init__(self):
        self.settings = get_settings()
        self.alembic_cfg = Config("alembic.ini")
        
    def get_database_url(self) -> str:
        """Obtient l'URL de la base de données selon l'environnement"""
        
        # 1. Priorité à DATABASE_URL en variable d'environnement
        if database_url := os.environ.get("DATABASE_URL"):
            logger.info("OK Utilisation de DATABASE_URL depuis les variables d'environnement")
            return database_url
            
        # 2. Configuration pour Cloud Run (via unix socket) - PAS de proxy nécessaire
        cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
        if cloud_sql_connection_name:
            postgres_user = os.environ.get("POSTGRES_USER", "skillforge_user")
            postgres_password = os.environ.get("POSTGRES_PASSWORD")
            postgres_db = os.environ.get("POSTGRES_DB", "skillforge_db")
            
            if postgres_password:
                database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@/{postgres_db}?host=/cloudsql/{cloud_sql_connection_name}"
                logger.info(f"OK Configuration Cloud Run avec unix socket: {postgres_user}@/cloudsql/{cloud_sql_connection_name}/{postgres_db}")
                return database_url
            
        # 3. Construction depuis les composants individuels (développement local)
        postgres_user = os.environ.get("POSTGRES_USER", "skillforge_user")
        postgres_password = os.environ.get("POSTGRES_PASSWORD")
        postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
        postgres_port = os.environ.get("POSTGRES_PORT", "5432")
        postgres_db = os.environ.get("POSTGRES_DB", "skillforge_db")
        
        if postgres_password:
            database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
            logger.info(f"OK URL construite depuis les composants: {postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}")
            return database_url
            
        # 4. Fallback pour le développement local
        if not self.settings.is_production:
            database_url = "sqlite+aiosqlite:///./skillforge_dev.db"
            logger.warning("WARNING Utilisation de SQLite pour le développement (aucun mot de passe PostgreSQL fourni)")
            return database_url
            
        raise ValueError("ERROR Aucune configuration de base de données trouvée. Définissez DATABASE_URL ou POSTGRES_PASSWORD")
    
    async def test_connection(self, database_url: str) -> bool:
        """Teste la connexion à la base de données"""
        try:
            engine = create_async_engine(database_url, echo=False)
            async with engine.connect() as conn:
                if "sqlite" in database_url:
                    await conn.execute(text("SELECT 1"))
                else:
                    await conn.execute(text("SELECT 1"))
            await engine.dispose()
            logger.info("OK Connexion à la base de données réussie")
            return True
        except Exception as e:
            logger.error(f"ERROR Erreur de connexion à la base de données: {e}")
            logger.error(f"DEBUG URL utilisée: {database_url}")
            
            # Informations de debug pour CI/CD
            import socket
            try:
                # Test de résolution DNS
                host_port = database_url.split('@')[1].split('/')[0] if '@' in database_url else 'localhost:5432'
                host = host_port.split(':')[0]
                port = int(host_port.split(':')[1]) if ':' in host_port else 5432
                
                logger.error(f"DEBUG Tentative de résolution DNS pour {host}...")
                socket.gethostbyname(host)
                logger.error(f"DEBUG DNS OK pour {host}")
                
                logger.error(f"DEBUG Test de connexion TCP {host}:{port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    logger.error(f"DEBUG Port {port} accessible sur {host}")
                else:
                    logger.error(f"DEBUG Port {port} inaccessible sur {host} (code: {result})")
                    
            except Exception as debug_e:
                logger.error(f"DEBUG Erreur lors du diagnostic: {debug_e}")
            
            return False
    
    def run_migrations(self, database_url: str):
        """Exécute les migrations Alembic"""
        try:
            # Configure l'URL de la base de données pour Alembic
            # Convertir les URLs async en sync pour Alembic
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")
            
            self.alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
            
            logger.info("Vérification de l'état actuel des migrations...")
            
            # Vérifie l'état actuel
            try:
                command.current(self.alembic_cfg)
            except Exception as e:
                logger.warning(f"Impossible de vérifier l'état actuel: {e}")
            
            logger.info("Exécution des migrations...")
            
            # Exécute les migrations
            command.upgrade(self.alembic_cfg, "head")
            
            logger.info("Migrations exécutées avec succès!")
            
            # Affiche l'état final
            logger.info("État final des migrations:")
            command.current(self.alembic_cfg, verbose=True)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des migrations: {e}")
            raise
    
    async def run(self):
        """Point d'entrée principal"""
        logger.info("INFO Démarrage de la migration automatique SkillForge User Service")
        logger.info(f"ENV Environnement: {self.settings.ENVIRONMENT}")
        
        try:
            # 1. Obtenir l'URL de la base de données
            database_url = self.get_database_url()
            
            # 2. Tester la connexion
            logger.info("TEST Test de la connexion à la base de données...")
            if not await self.test_connection(database_url):
                raise Exception("Impossible de se connecter à la base de données")
            
            # 3. Exécuter les migrations
            self.run_migrations(database_url)
            
            logger.info("SUCCESS Migration automatique terminée avec succès!")
            
        except Exception as e:
            logger.error(f"FAILED Échec de la migration: {e}")
            sys.exit(1)


async def main():
    """Point d'entrée du script"""
    migrator = DatabaseMigrator()
    await migrator.run()


if __name__ == "__main__":
    print("""
    SkillForge User Service - Migration Automatique
    ================================================
    
    Ce script migre automatiquement la base de données selon l'environnement:
    
    Variables d'environnement supportées:
    - DATABASE_URL: URL complète de la base de données (priorité)
    - POSTGRES_USER: Utilisateur PostgreSQL (défaut: skillforge_user)
    - POSTGRES_PASSWORD: Mot de passe PostgreSQL (requis pour PostgreSQL)
    - POSTGRES_HOST: Hôte PostgreSQL (défaut: localhost)
    - POSTGRES_PORT: Port PostgreSQL (défaut: 5432)
    - POSTGRES_DB: Base de données PostgreSQL (défaut: skillforge_db)
    
    Exemples d'utilisation:
    
    # Cloud SQL (via proxy sur port 5433)
    DATABASE_URL="postgresql+asyncpg://skillforge_user:password@localhost:5433/skillforge_db" python run_migrations.py
    
    # PostgreSQL local
    POSTGRES_PASSWORD="your_secure_password" python run_migrations.py
    
    # Développement avec SQLite (fallback)
    python run_migrations.py
    """)
    
    asyncio.run(main())