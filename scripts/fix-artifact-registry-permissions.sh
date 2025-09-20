#!/bin/bash
# Script pour corriger les permissions Artifact Registry
set -e

PROJECT_ID="skillforge-ai-mvp-25"
echo "🔐 Correction des permissions Artifact Registry"
echo "=============================================="
echo "Project: $PROJECT_ID"
echo ""

# Service account probable basé sur les patterns standards
SERVICE_ACCOUNT_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Vérifier si le service account existe
echo "📝 Vérification du service account..."
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ Service account trouvé"
else
    echo "❌ Service account non trouvé. Alternatives possibles:"
    gcloud iam service-accounts list --project="$PROJECT_ID" --filter="email:*github*" --format="value(email)"
    echo ""
    echo "Entrez l'email correct du service account:"
    read -p "Service Account Email: " SERVICE_ACCOUNT_EMAIL
fi

echo ""
echo "📝 Ajout des permissions Artifact Registry..."

# Permissions spécifiques pour Artifact Registry
REGISTRY_ROLES=(
    "roles/artifactregistry.admin"
    "roles/artifactregistry.writer"
)

for role in "${REGISTRY_ROLES[@]}"; do
    echo "  Adding: $role"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --condition=None 2>/dev/null || echo "    (already exists)"
done

echo ""
echo "📝 Permissions spécifiques au repository..."

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
echo "✅ Permissions Artifact Registry corrigées !"
echo ""

echo "🧪 Test des permissions..."
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL" | grep -i artifact || echo "Aucune permission Artifact Registry trouvée au niveau projet"

echo ""
echo "🎯 Repository permissions:"
gcloud artifacts repositories get-iam-policy "$REPO_NAME" \
    --location="$REGION" \
    --project="$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role,bindings.members)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL" || echo "Aucune permission trouvée au niveau repository"

echo ""
echo "✅ Terminé ! Relancez maintenant le workflow deploy-user-service.yml"