#!/bin/bash
# Script pour ajouter les permissions manquantes au service account CI/CD
set -e

PROJECT_ID="skillforge-ai-mvp-25"
SERVICE_ACCOUNT_EMAIL="${GCP_CICD_SERVICE_ACCOUNT}"

echo "🔐 Ajout des permissions pour le service account CI/CD"
echo "===================================================="
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

if [[ -z "$SERVICE_ACCOUNT_EMAIL" ]]; then
    echo "❌ Variable GCP_CICD_SERVICE_ACCOUNT non définie"
    echo "Utilisez: export GCP_CICD_SERVICE_ACCOUNT=your-sa@$PROJECT_ID.iam.gserviceaccount.com"
    exit 1
fi

# Rôles requis pour Terraform
REQUIRED_ROLES=(
    "roles/compute.admin"              # Réseaux, Load Balancer, SSL
    "roles/secretmanager.admin"        # Secret Manager complet
    "roles/storage.admin"              # Storage buckets
    "roles/artifactregistry.admin"     # Artifact Registry
    "roles/cloudsql.admin"             # Cloud SQL
    "roles/redis.admin"                # Redis
    "roles/run.admin"                  # Cloud Run
    "roles/monitoring.admin"           # Monitoring et dashboards
    "roles/iam.serviceAccountUser"     # Utiliser d'autres SAs
    "roles/resourcemanager.projectIamAdmin" # IAM policies
)

echo "📝 Ajout des rôles..."
for role in "${REQUIRED_ROLES[@]}"; do
    echo "  Adding: $role"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --condition=None 2>/dev/null || echo "    (already exists)"
done

echo ""
echo "✅ Permissions ajoutées avec succès !"
echo ""
echo "🧪 Test des permissions..."
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL"

echo ""
echo "🎯 Prochaines étapes :"
echo "1. Relancez le workflow Terraform"
echo "2. Ou testez directement deploy-user-service.yml"