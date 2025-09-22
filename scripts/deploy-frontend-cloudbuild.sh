#!/bin/bash

# Script pour déployer les applications frontend avec Cloud Build
# Usage: ./deploy-frontend-cloudbuild.sh <app-name>

set -euo pipefail

APP_NAME="$1"
PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"

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

log_info "Déploiement de l'application: $APP_NAME avec Cloud Build"

cd "apps/frontend/$APP_NAME"

# Vérifier que cloudbuild.yaml existe
if [[ ! -f "cloudbuild.yaml" ]]; then
    log_error "cloudbuild.yaml introuvable pour $APP_NAME"
    exit 1
fi

# Lancement du build avec Cloud Build
log_info "Lancement du build Cloud Build..."
BUILD_ID=$(gcloud builds submit --config=cloudbuild.yaml --gcs-source-staging-dir=gs://skillforge-cloudbuild-source/source . --format="value(id)") || {
    log_error "Échec du Cloud Build"
    exit 1
}

log_info "Cloud Build lancé avec ID: $BUILD_ID"

# Attendre la fin du build
log_info "Attente de la fin du build..."
gcloud builds log "$BUILD_ID" --stream || {
    log_error "Échec du build ou erreur lors du suivi des logs"
    exit 1
}

# Vérifier le statut final
BUILD_STATUS=$(gcloud builds describe "$BUILD_ID" --format="value(status)")
if [[ "$BUILD_STATUS" != "SUCCESS" ]]; then
    log_error "Build échoué avec le statut: $BUILD_STATUS"
    exit 1
fi

log_success "Build terminé avec succès"

# Récupération de l'URL du service
SERVICE_NAME="skillforge-$APP_NAME"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --format='value(status.url)' 2>/dev/null || echo "")

if [[ -n "$SERVICE_URL" ]]; then
    log_success "Service déployé: $SERVICE_URL"
    
    # Test du service
    log_info "Test du service..."
    sleep 15  # Attendre que le service soit prêt
    
    if curl -f -s "$SERVICE_URL/health" > /dev/null 2>&1; then
        log_success "Health check OK"
    else
        log_info "Test de la page principale..."
        if curl -f -s "$SERVICE_URL" > /dev/null 2>&1; then
            log_success "Page principale OK"
        else
            log_error "Service non accessible"
        fi
    fi
else
    log_error "Impossible de récupérer l'URL du service"
fi

echo ""
echo "=== RÉSUMÉ ==="
echo "Application: $APP_NAME"
echo "Service: $SERVICE_NAME"
echo "URL: $SERVICE_URL"
echo "Build ID: $BUILD_ID"
echo ""
if [[ -n "$SERVICE_URL" ]]; then
    echo "Pour mettre à jour la configuration Module Federation:"
    echo "URL Remote Entry: $SERVICE_URL/assets/remoteEntry.js"
fi

# Retour au répertoire racine
cd ../../..