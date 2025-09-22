import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.models.base import SQLModel

# Import all models so Alembic can detect them
from app.models.user import User, UserSettings, UserSession
# Company models moved to company-service
# from app.models.company import CompanyProfile, TeamMember, Subscription

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_database_url():
    """Get database URL from environment or config with secrets support."""
    # 1. Priorité à DATABASE_URL en variable d'environnement
    if database_url := os.environ.get("DATABASE_URL"):
        return database_url
        
    # 2. Configuration pour Cloud Run (via unix socket)
    cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
    if cloud_sql_connection_name:
        postgres_user = os.environ.get("POSTGRES_USER", "skillforge_user")
        postgres_password = os.environ.get("POSTGRES_PASSWORD")
        postgres_db = os.environ.get("POSTGRES_DB", "skillforge_db")
        
        if postgres_password:
            return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@/{postgres_db}?host=/cloudsql/{cloud_sql_connection_name}"
    
    # 3. Construction depuis les composants individuels avec secrets (local/dev)
    postgres_user = os.environ.get("POSTGRES_USER", "skillforge_user")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("POSTGRES_PORT", "5432")
    postgres_db = os.environ.get("POSTGRES_DB", "skillforge_db")
    
    if postgres_password:
        return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    # 4. Fallback pour développement local avec SQLite
    settings = get_settings()
    if not settings.is_production:
        return "sqlite+aiosqlite:///./skillforge_dev.db"
        
    # 5. Erreur si pas de configuration en production
    raise ValueError("DATABASE_URL or POSTGRES_PASSWORD must be set in production environment")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = AsyncEngine(
        engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Pour les migrations automatiques, utiliser la version synchrone
    from sqlalchemy import engine_from_config
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    # Convertir les URLs async en sync pour Alembic
    sync_url = configuration["sqlalchemy.url"]
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
    sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")
    configuration["sqlalchemy.url"] = sync_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()