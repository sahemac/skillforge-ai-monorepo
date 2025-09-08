#!/bin/bash

# Script pour vérifier et déployer le service user-service
set -e

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"
SERVICE_NAME="user-service-staging"
REPO_NAME="skillforge-docker-repo-staging"

echo "🔍 Vérification du service Cloud Run..."
echo "========================================="

# 1. Obtenir l'URL actuelle du service
echo "📍 Récupération de l'URL du service..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)' 2>/dev/null || echo "Service non trouvé")

if [ "$SERVICE_URL" == "Service non trouvé" ]; then
  echo "❌ Service $SERVICE_NAME n'existe pas encore"
else
  echo "✅ Service trouvé: $SERVICE_URL"
  
  # Test de santé
  echo "🧪 Test du endpoint /health..."
  curl -I "$SERVICE_URL/health" 2>/dev/null || echo "Endpoint /health inaccessible"
fi

# 2. Vérifier les images Docker disponibles
echo ""
echo "🐳 Images Docker disponibles..."
echo "========================================="
gcloud artifacts docker images list \
  $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME \
  --project=$PROJECT_ID \
  --limit=5 \
  --sort-by=~CREATE_TIME

# 3. Options de déploiement
echo ""
echo "📦 Options de déploiement:"
echo "========================================="
echo "1. Via GitHub Actions (Recommandé):"
echo "   - Aller sur GitHub → Actions → deploy-user-service.yml"
echo "   - Cliquer 'Run workflow'"
echo "   - Sélectionner 'staging'"
echo ""
echo "2. Déploiement manuel avec image existante:"
echo "   LATEST_IMAGE=\$(gcloud artifacts docker images list \ "
echo "     $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME \ "
echo "     --limit=1 --format='value(IMAGE)')"
echo ""
echo "   gcloud run deploy $SERVICE_NAME \ "
echo "     --image=\$LATEST_IMAGE \ "
echo "     --region=$REGION \ "
echo "     --project=$PROJECT_ID"
echo ""
echo "3. Build et deploy local (si code source disponible):"
echo "   cd apps/backend/user-service"
echo "   docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/user-service:latest ."
echo "   docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/user-service:latest"
echo "   gcloud run deploy $SERVICE_NAME --image=..."