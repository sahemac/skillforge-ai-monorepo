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
from typing import Optional, Dict, Any
# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Gestionnaire de migrations automatiques pour la base de données"""

    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")

    def get_database_url(self) -> str:
        """Obtient l'URL de la base de données selon l'environnement"""

        # 1. Priorité à DATABASE_URL en variable d'environnement
        if database_url := os.environ.get("DATABASE_URL"):
            logger.info("OK Utilisation de DATABASE_URL depuis les variables d'environnement")
            return database_url

        # 2. Construction depuis les composants individuels
        postgres_user = os.environ.get("POSTGRES_USER", "skillforge_user")
        postgres_password = os.environ.get("POSTGRES_PASSWORD")
        postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
        postgres_port = os.environ.get("POSTGRES_PORT", "5432")
        postgres_db = os.environ.get("POSTGRES_DB", "skillforge_db")

        if postgres_password:
            database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
            logger.info(f"OK URL construite depuis les composants: {postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}")
            return database_url

        # 3. Fallback pour le développement local
        logger.warning("WARNING Utilisation de SQLite pour le développement (aucun mot de passe PostgreSQL fourni)")
        return "sqlite+aiosqlite:///./skillforge_dev.db"

    def parse_database_url(self, database_url: str) -> Dict[str, Any]:
        """Parse l'URL de la base de données pour obtenir les composants"""
        parsed = urlparse(database_url)

        scheme = parsed.scheme
        if "+" in scheme:
            driver, db_type = scheme.split("+")
        else:
            driver, db_type = None, scheme

        user_pass = parsed.netloc.split("@")[0] if "@" in parsed.netloc else parsed.netloc
        user, password = user_pass.split(":") if ":" in user_pass else (user_pass, None)

        host_port = parsed.netloc.split("@")[-1] if "@" in parsed.netloc else parsed.netloc
        host, port = host_port.split(":") if ":" in host_port else (host_port, None)

        path = parsed.path[1:]  # Remove leading slash

        return {
            "driver": driver,
            "db_type": db_type,
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "path": path
        }

    async def test_connection(self, database_url: str) -> bool:
        """Teste la connexion à la base de données"""
        try:
            engine = create_async_engine(database_url, echo=False)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            logger.info("OK Connexion à la base de données réussie")
            return True
        except Exception as e:
            logger.error(f"ERROR Erreur de connexion à la base de données: {e}")
            logger.error(f"DEBUG URL utilisée: {database_url}")

            # Informations de debug pour CI/CD
            try:
                parsed = self.parse_database_url(database_url)
                host = parsed["host"]
                port = int(parsed["port"]) if parsed["port"] else 5432

                logger.error(f"DEBUG Tentative de résolution DNS pour {host}...")
                import socket
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
            # Convertir les URLs async en sync pour Alembic
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")

            self.alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

            logger.info("Vérification de l'état actuel des migrations...")
            try:
                command.current(self.alembic_cfg)
            except Exception as e:
                logger.warning(f"Impossible de vérifier l'état actuel: {e}")

            logger.info("Exécution des migrations...")
            command.upgrade(self.alembic_cfg, "head")

            logger.info("Migrations exécutées avec succès!")
            logger.info("État final des migrations:")
            command.current(self.alembic_cfg, verbose=True)

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des migrations: {e}")
            raise

    async def run(self):
        """Point d'entrée principal"""
        logger.info("INFO Démarrage de la migration automatique SkillForge User Service")
        logger.info(f"ENV Environnement: {os.environ.get('ENVIRONMENT', 'development')}")

        try:
            # 1. Obtenir l'URL de la base de données
            database_url = self.get_database_url()
            logger.info(f"DEBUG URL de la base de données: {database_url}")

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

    # Cloud SQL (via proxy sur port 5432)
    DATABASE_URL="postgresql+asyncpg://skillforge_user:password@localhost:5432/skillforge_db" python run_migrations.py

    # PostgreSQL local
    POSTGRES_PASSWORD="your_secure_password" python run_migrations.py

    # Développement avec SQLite (fallback)
    python run_migrations.py
    """)

    asyncio.run(main())