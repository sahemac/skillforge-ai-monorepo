#!/bin/bash

# Script de déploiement des services frontend SkillForge AI sur Cloud Run
# Déploie les 5 applications micro-frontend avec Module Federation

set -euo pipefail

# Configuration
PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"
REGISTRY="gcr.io/$PROJECT_ID"
VERSION=$(date +%Y%m%d-%H%M%S)

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Applications à déployer
declare -A APPS=(
    ["shell"]="3000"
    ["auth"]="3001"
    ["learner"]="3002"
    ["company"]="3003"
    ["admin"]="3004"
)

# URLs des services déployés (seront mises à jour après déploiement)
declare -A SERVICE_URLS

# Fonction pour vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI n'est pas installé"
        exit 1
    fi
    
    # Vérifier l'authentification
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Aucun compte Google Cloud actif. Exécutez: gcloud auth login"
        exit 1
    fi
    
    # Vérifier le projet
    if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
        log_error "Projet $PROJECT_ID introuvable"
        exit 1
    fi
    
    # Configurer le projet
    gcloud config set project "$PROJECT_ID"
    
    # Activer les APIs nécessaires
    log_info "Activation des APIs Google Cloud..."
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        compute.googleapis.com
    
    log_success "Prérequis vérifiés"
}

# Fonction pour nettoyer les anciennes images
cleanup_old_images() {
    local app_name="$1"
    log_info "Nettoyage des anciennes images pour $app_name..."
    
    # Garder les 3 dernières versions
    gcloud container images list-tags "$REGISTRY/skillforge-$app_name" \
        --limit=999 --sort-by=TIMESTAMP \
        --format="get(digest)" | tail -n +4 | while read digest; do
        if [ -n "$digest" ]; then
            gcloud container images delete "$REGISTRY/skillforge-$app_name@$digest" --quiet || true
        fi
    done
}

# Fonction pour créer les fichiers de configuration pour Module Federation
create_module_federation_configs() {
    log_info "Création des configurations Module Federation pour production..."
    
    # URLs de production qui seront utilisées
    local shell_url="https://skillforge-shell-${RANDOM_SUFFIX}-ew.a.run.app"
    local auth_url="https://skillforge-auth-${RANDOM_SUFFIX}-ew.a.run.app"
    local learner_url="https://skillforge-learner-${RANDOM_SUFFIX}-ew.a.run.app"
    local company_url="https://skillforge-company-${RANDOM_SUFFIX}-ew.a.run.app"
    local admin_url="https://skillforge-admin-${RANDOM_SUFFIX}-ew.a.run.app"
    
    # Mise à jour de la configuration shell pour pointer vers les services de production
    cat > "apps/frontend/shell/src/module-federation.config.ts" << EOF
export const moduleRemotes = {
  auth: '${auth_url}/assets/remoteEntry.js',
  learner: '${learner_url}/assets/remoteEntry.js',
  company: '${company_url}/assets/remoteEntry.js',
  admin: '${admin_url}/assets/remoteEntry.js',
};
EOF
}

# Fonction pour build et push une application
build_and_push_app() {
    local app_name="$1"
    local port="$2"
    local app_dir="apps/frontend/$app_name"
    
    log_info "Build et push de l'application $app_name..."
    
    # Vérifier que le répertoire existe
    if [ ! -d "$app_dir" ]; then
        log_error "Répertoire $app_dir introuvable"
        return 1
    fi
    
    # Build de l'image Docker
    local image_name="$REGISTRY/skillforge-$app_name:$VERSION"
    local latest_image="$REGISTRY/skillforge-$app_name:latest"
    
    log_info "Construction de l'image Docker: $image_name"
    
    # Construction avec Cloud Build pour de meilleures performances
    gcloud builds submit \
        --tag="$image_name" \
        --timeout=20m \
        "$app_dir" || {
        log_error "Échec du build pour $app_name"
        return 1
    }
    
    # Tag de l'image comme latest
    gcloud container images add-tag "$image_name" "$latest_image" --quiet
    
    log_success "Image $app_name construite et pushée"
    
    # Nettoyage des anciennes images
    cleanup_old_images "$app_name"
}

# Fonction pour déployer un service Cloud Run
deploy_cloud_run_service() {
    local app_name="$1"
    local port="$2"
    local image_name="$REGISTRY/skillforge-$app_name:$VERSION"
    local service_name="skillforge-$app_name"
    
    log_info "Déploiement du service Cloud Run: $service_name"
    
    # Variables d'environnement spécifiques à chaque app
    local env_vars=""
    case "$app_name" in
        "shell")
            env_vars="--set-env-vars=NODE_ENV=production,APP_TYPE=shell,MODULE_FEDERATION_HOST=true"
            ;;
        "auth")
            env_vars="--set-env-vars=NODE_ENV=production,APP_TYPE=auth,MODULE_FEDERATION_REMOTE=true"
            ;;
        "learner")
            env_vars="--set-env-vars=NODE_ENV=production,APP_TYPE=learner,MODULE_FEDERATION_REMOTE=true"
            ;;
        "company")
            env_vars="--set-env-vars=NODE_ENV=production,APP_TYPE=company,MODULE_FEDERATION_REMOTE=true"
            ;;
        "admin")
            env_vars="--set-env-vars=NODE_ENV=production,APP_TYPE=admin,MODULE_FEDERATION_REMOTE=true"
            ;;
    esac
    
    # Déploiement sur Cloud Run
    gcloud run deploy "$service_name" \
        --image="$image_name" \
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
        $env_vars \
        --add-cloudsql-instances="$PROJECT_ID:$REGION:skillforge-pg-instance-staging" \
        --labels="app=skillforge,component=frontend,type=$app_name,environment=production" \
        --quiet || {
        log_error "Échec du déploiement pour $service_name"
        return 1
    }
    
    # Récupération de l'URL du service
    local service_url=$(gcloud run services describe "$service_name" \
        --platform=managed \
        --region="$REGION" \
        --format='value(status.url)')
    
    SERVICE_URLS["$app_name"]="$service_url"
    
    log_success "Service $service_name déployé: $service_url"
}

# Fonction pour configurer le Load Balancer
configure_load_balancer() {
    log_info "Configuration du Load Balancer..."
    
    # Création des backend services pour chaque application frontend
    for app in "${!APPS[@]}"; do
        local service_name="skillforge-$app"
        local backend_service="skillforge-$app-backend"
        
        # Création du NEG (Network Endpoint Group) pour Cloud Run
        gcloud compute network-endpoint-groups create "$backend_service-neg" \
            --region="$REGION" \
            --network-endpoint-type=serverless \
            --cloud-run-service="$service_name" \
            --quiet || true
        
        # Création du backend service
        gcloud compute backend-services create "$backend_service" \
            --global \
            --load-balancing-scheme=EXTERNAL_MANAGED \
            --protocol=HTTPS \
            --quiet || true
        
        # Ajout du NEG au backend service
        gcloud compute backend-services add-backend "$backend_service" \
            --global \
            --network-endpoint-group="$backend_service-neg" \
            --network-endpoint-group-region="$REGION" \
            --quiet || true
    done
    
    # Configuration des path matchers dans le Load Balancer existant
    # Ceci nécessiterait une configuration plus complexe selon votre Load Balancer existant
    log_warning "Configuration manuelle du Load Balancer nécessaire pour les nouveaux services"
}

# Fonction pour mettre à jour les configurations Module Federation
update_module_federation_configs() {
    log_info "Mise à jour des configurations Module Federation avec les vraies URLs..."
    
    # Mise à jour de la configuration shell
    if [ -n "${SERVICE_URLS[auth]}" ] && [ -n "${SERVICE_URLS[learner]}" ] && [ -n "${SERVICE_URLS[company]}" ] && [ -n "${SERVICE_URLS[admin]}" ]; then
        
        # Création du nouveau fichier de configuration Vite pour shell
        local shell_config="apps/frontend/shell/vite.config.production.ts"
        cat > "$shell_config" << EOF
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        auth: '${SERVICE_URLS[auth]}/assets/remoteEntry.js',
        learner: '${SERVICE_URLS[learner]}/assets/remoteEntry.js',
        company: '${SERVICE_URLS[company]}/assets/remoteEntry.js',
        admin: '${SERVICE_URLS[admin]}/assets/remoteEntry.js',
      },
      shared: {
        react: { singleton: true, requiredVersion: '^19.1.1' },
        'react-dom': { singleton: true, requiredVersion: '^19.1.1' },
        'react-router-dom': { singleton: true, requiredVersion: '^6.20.1' },
        '@skillforge-ai/core': { singleton: true },
        '@skillforge-ai/ui-kit': { singleton: true },
        '@skillforge-ai/api-client': { singleton: true },
        '@skillforge-ai/shared': { singleton: true },
      },
    }),
  ],
  build: {
    target: 'esnext',
    minify: 'terser',
    cssCodeSplit: false,
  },
  define: {
    __DEV__: JSON.stringify(false),
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
});
EOF
        
        log_success "Configuration Module Federation mise à jour"
    else
        log_warning "Certaines URLs de service manquent, configuration Module Federation non mise à jour"
    fi
}

# Fonction pour tester les services déployés
test_deployed_services() {
    log_info "Test des services déployés..."
    
    for app in "${!SERVICE_URLS[@]}"; do
        local url="${SERVICE_URLS[$app]}"
        log_info "Test du service $app: $url"
        
        # Health check
        if curl -f -s "$url/health" > /dev/null; then
            log_success "✓ $app health check OK"
        else
            log_warning "✗ $app health check échoué"
        fi
        
        # Test de la page principale
        if curl -f -s "$url" > /dev/null; then
            log_success "✓ $app page principale OK"
        else
            log_warning "✗ $app page principale échouée"
        fi
    done
}

# Fonction pour afficher le résumé du déploiement
show_deployment_summary() {
    log_info "=== RÉSUMÉ DU DÉPLOIEMENT ==="
    echo ""
    echo "Version déployée: $VERSION"
    echo "Région: $REGION"
    echo "Projet: $PROJECT_ID"
    echo ""
    echo "Services déployés:"
    for app in "${!SERVICE_URLS[@]}"; do
        echo "  - $app: ${SERVICE_URLS[$app]}"
    done
    echo ""
    log_info "Pour accéder à l'application:"
    log_info "URL principale (Shell): ${SERVICE_URLS[shell]}"
    echo ""
    log_info "Pour rollback si nécessaire:"
    for app in "${!APPS[@]}"; do
        echo "  gcloud run services update-traffic skillforge-$app --to-revisions=PREVIOUS=100 --region=$REGION"
    done
}

# Fonction principale
main() {
    log_info "=== DÉPLOIEMENT DES SERVICES FRONTEND SKILLFORGE AI ==="
    
    # Vérifier les prérequis
    check_prerequisites
    
    # Build et push de toutes les applications
    log_info "=== PHASE 1: BUILD ET PUSH DES IMAGES ==="
    for app in "${!APPS[@]}"; do
        build_and_push_app "$app" "${APPS[$app]}"
    done
    
    # Déploiement des services Cloud Run
    log_info "=== PHASE 2: DÉPLOIEMENT DES SERVICES CLOUD RUN ==="
    for app in "${!APPS[@]}"; do
        deploy_cloud_run_service "$app" "${APPS[$app]}"
    done
    
    # Mise à jour des configurations Module Federation
    log_info "=== PHASE 3: MISE À JOUR DES CONFIGURATIONS ==="
    update_module_federation_configs
    
    # Configuration du Load Balancer
    log_info "=== PHASE 4: CONFIGURATION DU LOAD BALANCER ==="
    configure_load_balancer
    
    # Tests des services déployés
    log_info "=== PHASE 5: TESTS DES SERVICES ==="
    test_deployed_services
    
    # Affichage du résumé
    show_deployment_summary
    
    log_success "=== DÉPLOIEMENT TERMINÉ AVEC SUCCÈS ==="
}

# Gestion des signaux pour un nettoyage propre
trap 'log_error "Déploiement interrompu"; exit 1' INT TERM

# Exécution du script principal
main "$@"