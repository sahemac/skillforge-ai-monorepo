#!/bin/bash

# Script pour mettre à jour tous les fichiers cloudbuild.yaml avec la configuration sécurisée
# Remplace les mots de passe en clair par les références Secrets Manager

set -e

# Répertoire de base
BASE_DIR="C:/Users/DELL/Documents/GitHub/skillforge-ai-monorepo"

# Liste des services backend
SERVICES=(
    "user-service"
    "content-service"
    "audit-service"
    "company-service"
    "analytics-service"
    "ai-orchestrator-service"
    "chat-messaging-service"
    "portfolio-service"
    "workflow-service"
    "matching-service"
    "integration-service"
    "payment-service"
    "localization-service"
    "evaluation-service"
    "notification-service"
    "search-service"
    "gamification-service"
    "recommendation-service"
    "scheduling-service"
    "project-service"
    "realtime-collaboration-service"
    "storage-service"
    "subscription-service"
)

echo "🔄 Mise à jour des fichiers cloudbuild.yaml avec configuration sécurisée"
echo "Répertoire de base: $BASE_DIR"
echo ""

# Fonction pour mettre à jour un fichier cloudbuild.yaml
update_cloudbuild_file() {
    local service_name=$1
    local service_label=$(echo "$service_name" | sed 's/-service$//')
    local cloudbuild_file="$BASE_DIR/apps/backend/$service_name/cloudbuild.yaml"
    
    echo "📝 Mise à jour: $service_name"
    echo "   Fichier: $cloudbuild_file"
    
    # Vérifier si le fichier existe
    if [ ! -f "$cloudbuild_file" ]; then
        echo "   ⚠️  Fichier non trouvé, ignoré"
        return 0
    fi
    
    # Faire une sauvegarde
    cp "$cloudbuild_file" "$cloudbuild_file.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   💾 Sauvegarde créée"
    
    # Ligne actuelle avec mot de passe en clair
    local old_line="      - '--set-env-vars=ENVIRONMENT=production,SERVICE_NAME=$service_name,POSTGRES_HOST=127.0.0.1,POSTGRES_PORT=5432,POSTGRES_DB=skillforge_db,POSTGRES_USER=skillforge_user,POSTGRES_PASSWORD=Psaumes@27,DATABASE_URL=postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db'"
    
    # Nouvelles lignes sécurisées
    local new_lines="      # Configuration des variables d'environnement sécurisées
      - '--set-env-vars=ENVIRONMENT=production,SERVICE_NAME=$service_name,POSTGRES_HOST=127.0.0.1,POSTGRES_PORT=5432,POSTGRES_DB=skillforge_db,POSTGRES_USER=skillforge_user'
      # Référence au secret pour le mot de passe PostgreSQL
      - '--set-secrets=POSTGRES_PASSWORD=postgres-password:latest'
      # Configuration de l'URL de base de données (le mot de passe sera injecté automatiquement)
      - '--update-env-vars=DATABASE_URL=postgresql+asyncpg://skillforge_user:\$\${POSTGRES_PASSWORD}@127.0.0.1:5432/skillforge_db'
      # Configuration Cloud SQL Proxy
      - '--add-cloudsql-instances=skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging'"
    
    # Effectuer le remplacement
    if grep -q "POSTGRES_PASSWORD=Psaumes@27" "$cloudbuild_file"; then
        # Créer un fichier temporaire avec les modifications
        awk -v old_line="$old_line" -v new_lines="$new_lines" '
        {
            if ($0 == old_line) {
                print new_lines
            } else {
                print $0
            }
        }' "$cloudbuild_file" > "$cloudbuild_file.tmp"
        
        # Remplacer le fichier original
        mv "$cloudbuild_file.tmp" "$cloudbuild_file"
        echo "   ✅ Configuration mise à jour avec succès"
    else
        echo "   ℹ️  Pas de mot de passe en clair trouvé, fichier probablement déjà mis à jour"
    fi
    
    echo ""
}

# Mettre à jour tous les services
echo "🔄 Début de la mise à jour des fichiers..."
echo ""

for service in "${SERVICES[@]}"; do
    update_cloudbuild_file "$service"
done

echo "🎉 Mise à jour terminée !"
echo ""
echo "📋 Résumé des modifications:"
echo "   - Mots de passe PostgreSQL supprimés des variables d'environnement"
echo "   - Références aux secrets Secrets Manager ajoutées"
echo "   - Configuration Cloud SQL Proxy ajoutée"
echo "   - Sauvegardes créées pour tous les fichiers modifiés"
echo ""
echo "🔍 Vérification des modifications:"
echo ""

# Vérifier les modifications
for service in "${SERVICES[@]}"; do
    cloudbuild_file="$BASE_DIR/apps/backend/$service/cloudbuild.yaml"
    if [ -f "$cloudbuild_file" ]; then
        if grep -q "postgres-password:latest" "$cloudbuild_file"; then
            echo "✅ $service: Configuration sécurisée détectée"
        elif grep -q "POSTGRES_PASSWORD=Psaumes@27" "$cloudbuild_file"; then
            echo "⚠️  $service: Mot de passe encore en clair"
        else
            echo "ℹ️  $service: Configuration non détectée"
        fi
    else
        echo "❌ $service: Fichier cloudbuild.yaml non trouvé"
    fi
done

echo ""
echo "🚀 Prochaines étapes:"
echo "1. Exécuter le script de mise à jour des services Cloud Run:"
echo "   bash scripts/update-cloud-run-services.sh"
echo ""
echo "2. Vérifier la configuration des services:"
echo "   bash scripts/verify-cloud-run-config.sh"
echo ""
echo "3. Tester la connectivité DB depuis un service déployé:"
echo "   python scripts/test-db-connectivity.py"