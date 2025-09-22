#!/bin/bash

# Script de build Docker pour SkillForge AI Admin App
# Usage: ./docker-build.sh [tag] [--push]

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="skillforge-admin"
DEFAULT_TAG="latest"
REGISTRY="gcr.io/skillforge-ai-mvp-25"
DOCKERFILE="Dockerfile"

# Parse arguments
TAG=${1:-$DEFAULT_TAG}
PUSH_FLAG=$2

# Validation des arguments
if [[ "$PUSH_FLAG" != "" && "$PUSH_FLAG" != "--push" ]]; then
    echo -e "${RED}Usage: $0 [tag] [--push]${NC}"
    exit 1
fi

# Fonctions utilitaires
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

# Construction de l'image
build_image() {
    local image_name="$REGISTRY/$APP_NAME:$TAG"
    
    log_info "Building Docker image: $image_name"
    log_info "Using Dockerfile: $DOCKERFILE"
    
    # Vérification de l'existence du Dockerfile
    if [[ ! -f "$DOCKERFILE" ]]; then
        log_error "Dockerfile not found: $DOCKERFILE"
        exit 1
    fi
    
    # Build avec contexte du monorepo
    cd ../../..
    
    # Build de l'image
    docker build \
        -f "apps/frontend/admin/$DOCKERFILE" \
        -t "$image_name" \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
        --build-arg VERSION=$TAG \
        apps/frontend/admin/
    
    if [[ $? -eq 0 ]]; then
        log_success "Image built successfully: $image_name"
    else
        log_error "Failed to build image"
        exit 1
    fi
    
    # Retour au répertoire de l'app
    cd apps/frontend/admin/
}

# Push de l'image
push_image() {
    local image_name="$REGISTRY/$APP_NAME:$TAG"
    
    log_info "Pushing image to registry: $image_name"
    
    # Vérification de l'authentification Docker
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker daemon not running or not accessible"
        exit 1
    fi
    
    # Push de l'image
    docker push "$image_name"
    
    if [[ $? -eq 0 ]]; then
        log_success "Image pushed successfully: $image_name"
    else
        log_error "Failed to push image"
        exit 1
    fi
}

# Informations de build
show_build_info() {
    log_info "=== Build Information ==="
    log_info "App Name: $APP_NAME"
    log_info "Tag: $TAG"
    log_info "Registry: $REGISTRY"
    log_info "Full Image Name: $REGISTRY/$APP_NAME:$TAG"
    log_info "Build Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log_info "Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"
    echo ""
}

# Affichage des informations d'utilisation
show_usage() {
    echo ""
    log_info "=== Usage Examples ==="
    echo "  Build latest version:"
    echo "    ./docker-build.sh"
    echo ""
    echo "  Build with specific tag:"
    echo "    ./docker-build.sh v1.0.0"
    echo ""
    echo "  Build and push to registry:"
    echo "    ./docker-build.sh v1.0.0 --push"
    echo ""
    echo "  Build and push latest:"
    echo "    ./docker-build.sh latest --push"
    echo ""
}

# Fonction principale
main() {
    log_info "Starting Docker build for SkillForge AI Admin App"
    
    show_build_info
    
    # Build de l'image
    build_image
    
    # Push si demandé
    if [[ "$PUSH_FLAG" == "--push" ]]; then
        push_image
    else
        log_warning "Image built locally. Use '--push' flag to push to registry."
    fi
    
    log_success "Build process completed successfully!"
    show_usage
}

# Gestion des signaux
trap 'log_error "Build interrupted"; exit 1' INT TERM

# Exécution du script principal
main "$@"