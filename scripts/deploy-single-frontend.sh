#!/bin/bash

# Script pour déployer une seule application frontend
# Usage: ./deploy-single-frontend.sh <app-name>

set -euo pipefail

APP_NAME="$1"
PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"
REGISTRY="gcr.io/$PROJECT_ID"
VERSION=$(date +%Y%m%d-%H%M%S)

# Couleurs pour les logs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que l'application existe
if [[ ! -d "apps/frontend/$APP_NAME" ]]; then
    log_error "Application $APP_NAME introuvable dans apps/frontend/"
    exit 1
fi

# Configuration gcloud
gcloud config set project "$PROJECT_ID"

log_info "Déploiement de l'application: $APP_NAME"
log_info "Version: $VERSION"

# Build de l'image
IMAGE_NAME="$REGISTRY/skillforge-$APP_NAME:$VERSION"
log_info "Construction de l'image: $IMAGE_NAME"

cd "apps/frontend/$APP_NAME"

# Build avec Cloud Build
gcloud builds submit \
    --tag="$IMAGE_NAME" \
    --timeout=20m \
    . || {
    log_error "Échec du build"
    exit 1
}

log_success "Image construite: $IMAGE_NAME"

# Déploiement sur Cloud Run
SERVICE_NAME="skillforge-$APP_NAME"
log_info "Déploiement du service: $SERVICE_NAME"

# Variables d'environnement spécifiques
ENV_VARS="NODE_ENV=production,APP_TYPE=$APP_NAME"
if [[ "$APP_NAME" == "shell" ]]; then
    ENV_VARS="$ENV_VARS,MODULE_FEDERATION_HOST=true"
else
    ENV_VARS="$ENV_VARS,MODULE_FEDERATION_REMOTE=true"
fi

gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --allow-unauthenticated \
    --port=80 \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=80 \
    --timeout=300 \
    --ingress=all \
    --set-env-vars="$ENV_VARS" \
    --labels="app=skillforge,component=frontend,type=$APP_NAME,environment=production" \
    --quiet || {
    log_error "Échec du déploiement"
    exit 1
}

# Récupération de l'URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --format='value(status.url)')

log_success "Service déployé: $SERVICE_URL"

# Test du service
log_info "Test du service..."
if curl -f -s "$SERVICE_URL/health" > /dev/null 2>&1; then
    log_success "Health check OK"
else
    log_error "Health check échoué"
fi

echo ""
echo "=== RÉSUMÉ ==="
echo "Application: $APP_NAME"
echo "Service: $SERVICE_NAME"
echo "URL: $SERVICE_URL"
echo "Image: $IMAGE_NAME"
echo "Version: $VERSION"