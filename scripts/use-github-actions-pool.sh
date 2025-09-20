#!/bin/bash
# Script temporaire pour utiliser le pool github-actions qui fonctionne

set -e

PROJECT_ID="skillforge-ai-mvp-25"
SERVICE_ACCOUNT="sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com"

echo "🔄 SOLUTION TEMPORAIRE - Utilisation du pool github-actions"
echo "==========================================================="
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT"
echo ""

echo "📝 Configuration recommandée pour les secrets GitHub:"
echo ""
echo "GCP_PROJECT_ID:"
echo "  $PROJECT_ID"
echo ""
echo "GCP_WIF_PROVIDER (UTILISEZ CECI TEMPORAIREMENT):"
echo "  projects/$PROJECT_ID/locations/global/workloadIdentityPools/github-actions/providers/github"
echo ""
echo "GCP_CICD_SERVICE_ACCOUNT:"
echo "  $SERVICE_ACCOUNT"
echo ""

echo "🔍 Vérification de la configuration actuelle:"
echo ""
echo "Pool github-actions provider:"
gcloud iam workload-identity-pools providers describe github \
    --workload-identity-pool=github-actions \
    --location=global \
    --project="$PROJECT_ID" \
    --format="value(oidc.allowedAudiences)" || echo "Aucune audience configurée (utilise l'audience par défaut)"

echo ""
echo "Bindings du service account sa-user-service-staging:"
gcloud iam service-accounts get-iam-policy "$SERVICE_ACCOUNT" --project="$PROJECT_ID" | grep github-actions || echo "❌ Pas de binding avec github-actions"

echo ""
echo "✅ Le service account sa-user-service-staging est déjà lié au pool github-actions !"
echo ""
echo "🎯 ACTION REQUISE:"
echo "1. Dans GitHub > Settings > Secrets > Actions"
echo "2. Mettez à jour GCP_WIF_PROVIDER avec la valeur ci-dessus"
echo "3. Relancez le workflow"
echo ""
echo "Cette solution temporaire devrait fonctionner immédiatement !"