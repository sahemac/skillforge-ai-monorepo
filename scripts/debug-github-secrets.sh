#!/bin/bash
# Script pour diagnostiquer la configuration des secrets GitHub et Workload Identity

set -e

PROJECT_ID="skillforge-ai-mvp-25"

echo "🔍 DIAGNOSTIC - Configuration GitHub Actions et Workload Identity"
echo "================================================================="
echo "Project: $PROJECT_ID"
echo ""

echo "📋 1. POOLS ET PROVIDERS WORKLOAD IDENTITY"
echo "-------------------------------------------"
echo "Pools disponibles:"
gcloud iam workload-identity-pools list --location=global --project="$PROJECT_ID" --format="table(name,displayName,state)"

echo ""
echo "Providers dans skillforge-pool:"
gcloud iam workload-identity-pools providers list --workload-identity-pool=skillforge-pool --location=global --project="$PROJECT_ID" --format="table(name,displayName,state)"

echo ""
echo "Providers dans github-actions:"
gcloud iam workload-identity-pools providers list --workload-identity-pool=github-actions --location=global --project="$PROJECT_ID" --format="table(name,displayName,state)"

echo ""
echo "📋 2. SERVICE ACCOUNTS ET BINDINGS"
echo "-----------------------------------"
echo "Service accounts:"
gcloud iam service-accounts list --project="$PROJECT_ID" --format="table(email,displayName)"

echo ""
echo "Bindings sa-user-service-staging:"
gcloud iam service-accounts get-iam-policy sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com --project="$PROJECT_ID"

echo ""
echo "Bindings sa-github-actions-cicd:"
gcloud iam service-accounts get-iam-policy sa-github-actions-cicd@skillforge-ai-mvp-25.iam.gserviceaccount.com --project="$PROJECT_ID" 2>/dev/null || echo "(No bindings or access denied)"

echo ""
echo "📋 3. VALEURS CORRECTES POUR LES SECRETS GITHUB"
echo "------------------------------------------------"
echo "Basé sur votre configuration, les secrets GitHub devraient être:"
echo ""
echo "GCP_PROJECT_ID:"
echo "  $PROJECT_ID"
echo ""
echo "GCP_WIF_PROVIDER (recommandé - skillforge-pool):"
echo "  projects/$PROJECT_ID/locations/global/workloadIdentityPools/skillforge-pool/providers/github-provider"
echo ""
echo "GCP_CICD_SERVICE_ACCOUNT:"
echo "  sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com"
echo ""
echo "Alternative - si vous voulez utiliser github-actions pool:"
echo "GCP_WIF_PROVIDER (alternative):"
echo "  projects/$PROJECT_ID/locations/global/workloadIdentityPools/github-actions/providers/github"
echo ""

echo "📋 4. PERMISSIONS ARTIFACT REGISTRY"
echo "------------------------------------"
echo "Permissions sa-user-service-staging sur le projet:"
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com" | head -20

echo ""
echo "Test d'accès au repository Artifact Registry:"
gcloud artifacts repositories describe skillforge-docker-repo-staging \
    --location=europe-west1 \
    --project="$PROJECT_ID" \
    --format="value(name,createTime)" 2>/dev/null || echo "❌ Accès refusé ou repository non trouvé"

echo ""
echo "✅ DIAGNOSTIC TERMINÉ"
echo "====================="
echo ""
echo "🎯 ACTIONS À PRENDRE:"
echo "1. Vérifiez que vos secrets GitHub correspondent aux valeurs ci-dessus"
echo "2. Si le problème persiste, essayez d'utiliser le pool 'github-actions' à la place"
echo "3. Vérifiez que le workflow utilise bien la bonne audience dans l'auth step"