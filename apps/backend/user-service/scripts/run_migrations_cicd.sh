#!/bin/bash
# Script de migration automatique pour CI/CD
# Gère les secrets Google Cloud et Cloud SQL

set -e

echo "🚀 SkillForge User Service - Migration CI/CD"
echo "============================================"

# Variables par défaut
PROJECT_ID=${GCP_PROJECT_ID:-"skillforge-ai-mvp-25"}
INSTANCE_CONNECTION_NAME="${PROJECT_ID}:europe-west1:skillforge-pg-instance-staging"
DB_USER=${DB_USER:-"skillforge_user"}
DB_NAME=${DB_NAME:-"skillforge_db"}

echo "📋 Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Instance: $INSTANCE_CONNECTION_NAME"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"

# Function to get database password from Secret Manager
get_db_password() {
    echo "🔐 Récupération du mot de passe depuis Secret Manager..."
    if command -v gcloud >/dev/null 2>&1; then
        gcloud secrets versions access latest --secret="postgres-password" --project="$PROJECT_ID" 2>/dev/null || {
            echo "⚠️  Impossible de récupérer le secret, utilisation de POSTGRES_PASSWORD"
            echo "${POSTGRES_PASSWORD}"
        }
    else
        echo "⚠️  gcloud CLI non disponible, utilisation de POSTGRES_PASSWORD"
        echo "${POSTGRES_PASSWORD}"
    fi
}

# Function to run migrations with Cloud SQL
run_migrations_cloud_sql() {
    echo "☁️  Migration avec Cloud SQL..."
    
    # Récupérer le mot de passe
    DB_PASSWORD=$(get_db_password)
    
    if [[ -z "$DB_PASSWORD" ]]; then
        echo "❌ Aucun mot de passe de base de données trouvé"
        exit 1
    fi
    
    # Construire l'URL de la base de données
    # En CI/CD, on utilise l'adresse d'instance directe ou unix socket
    if [[ -n "$CLOUD_SQL_CONNECTION_NAME" ]]; then
        # Utilisation du socket Unix dans Cloud Run
        DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"
    else
        # Fallback vers l'adresse IP publique (moins sécurisé)
        DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST:-127.0.0.1}:5432/${DB_NAME}"
    fi
    
    echo "🔗 URL de connexion configurée"
    
    # Exporter les variables pour le script Python
    export DATABASE_URL
    export ENVIRONMENT="production"
    
    # Exécuter les migrations
    python run_migrations.py
}

# Function to run migrations with local PostgreSQL (for development)
run_migrations_local() {
    echo "🏠 Migration avec PostgreSQL local..."
    
    # Utiliser les variables d'environnement locales
    export POSTGRES_USER="${DB_USER}"
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-Psaumes@27}"
    export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
    export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    export POSTGRES_DB="${DB_NAME}"
    export ENVIRONMENT="${ENVIRONMENT:-development}"
    
    # Exécuter les migrations
    python run_migrations.py
}

# Main execution
main() {
    cd "$(dirname "$0")/.."
    
    echo "🔍 Détection de l'environnement..."
    
    # Vérifier si on est dans un environnement Cloud (Google Cloud Run)
    if [[ -n "$GOOGLE_CLOUD_PROJECT" ]] || [[ -n "$K_SERVICE" ]] || [[ "$ENVIRONMENT" == "production" ]]; then
        echo "☁️  Environnement Cloud détecté"
        run_migrations_cloud_sql
    else
        echo "🏠 Environnement local détecté"
        run_migrations_local
    fi
    
    echo "✅ Migrations terminées avec succès!"
}

# Help function
show_help() {
    cat << EOF
🚀 SkillForge User Service - Migration CI/CD

Usage: $0 [OPTIONS]

Variables d'environnement:
  GCP_PROJECT_ID              ID du projet Google Cloud (défaut: skillforge-ai-mvp-25)
  DB_USER                     Utilisateur de la base de données (défaut: skillforge_user)
  DB_NAME                     Nom de la base de données (défaut: skillforge_db)
  POSTGRES_PASSWORD           Mot de passe PostgreSQL (local)
  CLOUD_SQL_CONNECTION_NAME   Nom de connexion Cloud SQL (format: project:region:instance)
  ENVIRONMENT                 Environnement (development/production)

Exemples:
  # CI/CD avec Cloud SQL
  ENVIRONMENT=production ./scripts/run_migrations_cicd.sh
  
  # Local avec PostgreSQL
  POSTGRES_PASSWORD="password" ./scripts/run_migrations_cicd.sh
  
  # Local avec variables d'environnement
  DB_USER=user DB_NAME=mydb ./scripts/run_migrations_cicd.sh

EOF
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main
        ;;
esac