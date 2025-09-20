#!/bin/bash
# Script pour corriger les permissions du service account sa-user-service-staging
set -e

PROJECT_ID="skillforge-ai-mvp-25"
SERVICE_ACCOUNT_EMAIL="sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com"

echo "🔐 Correction des permissions pour sa-user-service-staging"
echo "========================================================"
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Permissions nécessaires pour CI/CD
REQUIRED_ROLES=(
    "roles/artifactregistry.writer"    # Pour pusher les images Docker
    "roles/run.admin"                  # Pour déployer sur Cloud Run
    "roles/cloudsql.client"           # Pour les migrations DB
    "roles/secretmanager.secretAccessor" # Pour accéder aux secrets
)

echo "📝 Ajout des rôles au niveau projet..."
for role in "${REQUIRED_ROLES[@]}"; do
    echo "  Adding: $role"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --condition=None 2>/dev/null || echo "    (already exists)"
done

echo ""
echo "📝 Permissions spécifiques au repository Artifact Registry..."

# Permissions sur le repository staging spécifique
REPO_NAME="skillforge-docker-repo-staging"
REGION="europe-west1"

echo "  Repository: $REPO_NAME"
gcloud artifacts repositories add-iam-policy-binding "$REPO_NAME" \
    --location="$REGION" \
    --project="$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/artifactregistry.writer" 2>/dev/null || echo "    (already exists)"

echo ""
echo "✅ Permissions corrigées !"
echo ""

echo "🧪 Vérification des permissions..."
echo "Permissions au niveau projet:"
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL"

echo ""
echo "Permissions au niveau repository:"
gcloud artifacts repositories get-iam-policy "$REPO_NAME" \
    --location="$REGION" \
    --project="$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role,bindings.members)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL" 2>/dev/null || echo "Aucune permission trouvée au niveau repository"

echo ""
echo "✅ Terminé ! Le workflow deploy-user-service.yml devrait maintenant fonctionner."
echo ""
echo "🎯 Prochaines étapes :"
echo "1. Relancez le workflow deploy-user-service.yml"
echo "2. Ou lancez manuellement le workflow sur GitHub Actions"