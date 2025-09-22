#!/bin/bash

# Script de déploiement manuel des applications frontend
# Usage: ./deploy-frontend-manual.sh

set -euo pipefail

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"
REGISTRY="gcr.io/$PROJECT_ID"

# Couleurs pour les logs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Applications à déployer
declare -A APPS=(
    ["auth"]="Authentification"
    ["learner"]="Interface Apprenants"
    ["company"]="Interface Entreprises"
    ["admin"]="Interface Administration"
    ["shell"]="Application Principale"
)

declare -A DEPLOYED_URLS

# Configuration gcloud
gcloud config set project "$PROJECT_ID"

log_info "=== DÉPLOIEMENT DES SERVICES FRONTEND SKILLFORGE AI ==="
echo ""

# Déployer directement sur Cloud Run avec des images existantes ou créer des services basiques
deploy_service() {
    local app_name="$1"
    local description="$2"
    local service_name="skillforge-$app_name"
    
    log_info "Déploiement de $description ($app_name)..."
    
    # Variables d'environnement
    local env_vars="NODE_ENV=production,APP_TYPE=$app_name"
    if [[ "$app_name" == "shell" ]]; then
        env_vars="$env_vars,MODULE_FEDERATION_HOST=true"
    else
        env_vars="$env_vars,MODULE_FEDERATION_REMOTE=true"
    fi
    
    # Utiliser une image nginx de base temporaire pour créer le service
    # L'image sera mise à jour plus tard avec le vrai build
    gcloud run deploy "$service_name" \
        --image="nginx:alpine" \
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
        --set-env-vars="$env_vars" \
        --labels="app=skillforge,component=frontend,type=$app_name,environment=production" \
        --quiet || {
        log_error "Échec du déploiement pour $service_name"
        return 1
    }
    
    # Récupération de l'URL
    local service_url=$(gcloud run services describe "$service_name" \
        --platform=managed \
        --region="$REGION" \
        --format='value(status.url)')
    
    DEPLOYED_URLS["$app_name"]="$service_url"
    
    log_success "$description déployé: $service_url"
    echo ""
}

# Déployer tous les services
log_info "Phase 1: Création des services Cloud Run avec images temporaires"
echo ""

for app in auth learner company admin shell; do
    deploy_service "$app" "${APPS[$app]}"
done

# Afficher les URLs pour la configuration Module Federation
log_info "=== CONFIGURATION MODULE FEDERATION ==="
echo ""
echo "URLs des services déployés:"
for app in "${!DEPLOYED_URLS[@]}"; do
    echo "  $app: ${DEPLOYED_URLS[$app]}"
done

echo ""
echo "Configuration pour vite.config.ts (shell):"
echo "remotes: {"
echo "  auth: '${DEPLOYED_URLS[auth]}/assets/remoteEntry.js',"
echo "  learner: '${DEPLOYED_URLS[learner]}/assets/remoteEntry.js',"
echo "  company: '${DEPLOYED_URLS[company]}/assets/remoteEntry.js',"
echo "  admin: '${DEPLOYED_URLS[admin]}/assets/remoteEntry.js',"
echo "},"

echo ""
log_warning "Les services utilisent actuellement des images nginx de base."
log_warning "Pour déployer les vraies applications, vous devrez:"
echo "1. Construire les images Docker localement"
echo "2. Les pusher vers GCR"
echo "3. Mettre à jour les services Cloud Run avec les nouvelles images"

echo ""
log_info "Commandes pour mettre à jour avec de vraies images:"
for app in "${!APPS[@]}"; do
    echo "# Pour $app:"
    echo "docker build -t gcr.io/$PROJECT_ID/skillforge-$app:latest apps/frontend/$app/"
    echo "docker push gcr.io/$PROJECT_ID/skillforge-$app:latest"
    echo "gcloud run deploy skillforge-$app --image=gcr.io/$PROJECT_ID/skillforge-$app:latest --region=$REGION"
    echo ""
done

echo ""
log_info "=== TESTS DE CONNECTIVITÉ ==="
for app in "${!DEPLOYED_URLS[@]}"; do
    local url="${DEPLOYED_URLS[$app]}"
    echo "Testing $app: $url"
    if curl -f -s "$url" > /dev/null 2>&1; then
        log_success "✓ $app accessible"
    else
        log_warning "✗ $app non accessible (normal avec nginx de base)"
    fi
done

echo ""
log_info "=== RÉSUMÉ DU DÉPLOIEMENT ==="
echo "Projet: $PROJECT_ID"
echo "Région: $REGION"
echo "Services créés: ${#DEPLOYED_URLS[@]}"
echo ""
echo "URLs principales:"
echo "  Shell (App principale): ${DEPLOYED_URLS[shell]}"
echo "  Auth: ${DEPLOYED_URLS[auth]}"
echo "  Learner: ${DEPLOYED_URLS[learner]}"
echo "  Company: ${DEPLOYED_URLS[company]}"
echo "  Admin: ${DEPLOYED_URLS[admin]}"

echo ""
log_success "=== SERVICES CLOUD RUN CRÉÉS AVEC SUCCÈS ==="
log_info "Consultez le fichier DEPLOYMENT_GUIDE_FRONTEND.md pour les prochaines étapes"