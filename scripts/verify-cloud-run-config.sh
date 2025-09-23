#!/bin/bash

# Script de vérification de la configuration Cloud Run pour SkillForge AI
# Vérifie que les services sont correctement configurés avec Secrets Manager et Cloud SQL Proxy

set -e

# Configuration
PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"

echo "🔍 Vérification de la configuration Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Fonction pour vérifier un service
verify_service() {
    local service_name=$1
    echo "📋 Vérification du service: $service_name"
    
    # Vérifier si le service existe
    if ! gcloud run services describe "$service_name" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "⚠️  Service $service_name n'existe pas"
        return 0
    fi
    
    # Récupérer la configuration du service
    local service_config=$(gcloud run services describe "$service_name" --region="$REGION" --project="$PROJECT_ID" --format="json")
    
    # Vérifier Cloud SQL Proxy
    local cloud_sql_instances=$(echo "$service_config" | jq -r '.spec.template.metadata.annotations["run.googleapis.com/cloudsql-instances"] // "non-configuré"')
    echo "   Cloud SQL Instances: $cloud_sql_instances"
    
    # Vérifier les secrets
    local secrets=$(echo "$service_config" | jq -r '.spec.template.spec.template.spec.containers[0].env[]? | select(.valueFrom.secretKeyRef) | .name + "=" + .valueFrom.secretKeyRef.name + ":" + .valueFrom.secretKeyRef.key')
    if [ -n "$secrets" ]; then
        echo "   Secrets configurés:"
        echo "$secrets" | sed 's/^/     /'
    else
        echo "   ⚠️  Aucun secret configuré"
    fi
    
    # Vérifier les variables d'environnement sensibles
    local env_vars=$(echo "$service_config" | jq -r '.spec.template.spec.template.spec.containers[0].env[]? | select(.value) | .name + "=" + .value')
    if echo "$env_vars" | grep -q "PASSWORD"; then
        echo "   ⚠️  ATTENTION: Variables contenant PASSWORD en clair détectées!"
        echo "$env_vars" | grep PASSWORD | sed 's/^/     /'
    else
        echo "   ✅ Aucune variable sensible en clair détectée"
    fi
    
    # Status du service
    local status=$(echo "$service_config" | jq -r '.status.conditions[] | select(.type=="Ready") | .status')
    echo "   Status: $status"
    
    echo ""
}

# Liste des services à vérifier
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

# Vérifier tous les services
for service in "${SERVICES[@]}"; do
    verify_service "$service"
done

echo "🔐 Vérification du secret postgres-password..."
if gcloud secrets describe postgres-password --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ Secret postgres-password existe"
    
    # Vérifier les permissions
    local secret_policy=$(gcloud secrets get-iam-policy postgres-password --project="$PROJECT_ID" --format="json")
    local has_accessor=$(echo "$secret_policy" | jq -r '.bindings[]? | select(.role=="roles/secretmanager.secretAccessor") | .members[]?' | grep -q "compute@developer.gserviceaccount.com" && echo "true" || echo "false")
    
    if [ "$has_accessor" = "true" ]; then
        echo "✅ Service account a accès au secret"
    else
        echo "⚠️  Service account n'a pas accès au secret"
    fi
else
    echo "❌ Secret postgres-password n'existe pas"
fi

echo ""
echo "🏁 Vérification terminée!"
echo ""
echo "📋 Commandes utiles:"
echo "# Tester un service spécifique:"
echo "curl https://[SERVICE_NAME]-[HASH]-ew.a.run.app/health"
echo ""
echo "# Voir les logs d'un service:"
echo "gcloud logging read 'resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"[SERVICE_NAME]\"' --limit=50 --format='table(timestamp,jsonPayload.message)'"
echo ""
echo "# Exécuter le test de connectivité DB:"
echo "python scripts/test-db-connectivity.py"