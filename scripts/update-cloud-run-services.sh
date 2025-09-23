#!/bin/bash

# Script pour mettre à jour tous les services Cloud Run avec Cloud SQL Proxy et Secrets Manager
# Pour SkillForge AI Production

set -e

# Configuration
PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"
CLOUD_SQL_INSTANCE="skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging"

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

echo "🚀 Mise à jour des services Cloud Run avec Cloud SQL Proxy et Secrets Manager"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Cloud SQL Instance: $CLOUD_SQL_INSTANCE"
echo ""

# Fonction pour mettre à jour un service
update_service() {
    local service_name=$1
    echo "📦 Mise à jour du service: $service_name"
    
    # Vérifier si le service existe
    if ! gcloud run services describe "$service_name" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "⚠️  Service $service_name n'existe pas, ignoré"
        return 0
    fi
    
    # Mettre à jour le service avec Cloud SQL Proxy et Secrets Manager
    gcloud run services update "$service_name" \
        --add-cloudsql-instances="$CLOUD_SQL_INSTANCE" \
        --set-secrets="POSTGRES_PASSWORD=postgres-password:latest" \
        --update-env-vars="DATABASE_URL=postgresql+asyncpg://skillforge_user:\${POSTGRES_PASSWORD}@127.0.0.1:5432/skillforge_db" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ Service $service_name mis à jour avec succès"
    else
        echo "❌ Échec de la mise à jour du service $service_name"
        return 1
    fi
    
    echo ""
}

# Mettre à jour tous les services
echo "🔄 Début de la mise à jour des services..."
echo ""

for service in "${SERVICES[@]}"; do
    update_service "$service"
done

echo "🎉 Mise à jour terminée !"
echo ""
echo "🔍 Vérification des services mis à jour..."

# Vérification des services
for service in "${SERVICES[@]}"; do
    if gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(metadata.name)" >/dev/null 2>&1; then
        echo "✅ $service: Actif"
    else
        echo "❌ $service: Introuvable"
    fi
done

echo ""
echo "📋 Commandes utiles pour vérifier la configuration:"
echo ""
echo "# Vérifier les secrets d'un service:"
echo "gcloud run services describe [SERVICE_NAME] --region=$REGION --format='value(spec.template.spec.template.spec.containers[0].env[].valueFrom.secretKeyRef)'"
echo ""
echo "# Vérifier les instances Cloud SQL:"
echo "gcloud run services describe [SERVICE_NAME] --region=$REGION --format='value(spec.template.metadata.annotations)'"
echo ""
echo "# Tester la connectivité depuis un service:"
echo "gcloud run jobs execute test-db-connectivity --region=$REGION"