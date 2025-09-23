#!/bin/bash

# Script pour corriger les configurations cloudbuild.yaml avec les bonnes valeurs
# Corrige: registry, ingress settings, substitutions

set -e

PROJECT_ID="skillforge-ai-mvp-25"
CORRECT_REGISTRY="europe-west1-docker.pkg.dev/$PROJECT_ID/skillforge-ai-registry"
WRONG_REGISTRY="europe-west1-docker.pkg.dev/$PROJECT_ID/skillforge-docker-repo-staging"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Correction des configurations cloudbuild.yaml ===${NC}"

# Services à corriger (tous ceux avec cloudbuild.yaml)
SERVICES=(
    "user-service"
    "subscription-service"
    "payment-service"
    "notification-service"
    "content-service"
    "search-service"
    "project-service"
    "matching-service"
    "workflow-service"
    "audit-service"
    "portfolio-service"
    "evaluation-service"
    "chat-messaging-service"
    "realtime-collaboration-service"
    "recommendation-service"
    "ai-orchestrator-service"
    "storage-service"
    "scheduling-service"
    "gamification-service"
    "localization-service"
    "integration-service"
    "company-service"
    "analytics-service"
)

fix_cloudbuild_config() {
    local service=$1
    local config_file="apps/backend/$service/cloudbuild.yaml"
    
    if [ ! -f "$config_file" ]; then
        echo -e "${RED}❌ Config non trouvé: $config_file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Correction: $service${NC}"
    
    # Backup
    cp "$config_file" "$config_file.backup"
    
    # Corrections avec sed
    sed -i "s|$WRONG_REGISTRY|$CORRECT_REGISTRY|g" "$config_file"
    sed -i "s|--ingress=all|--ingress=internal-and-cloud-load-balancing|g" "$config_file"
    sed -i "s|'$service'|\${_SERVICE_NAME}|g" "$config_file"
    
    # Ajouter substitutions si manquantes
    if ! grep -q "substitutions:" "$config_file"; then
        echo "" >> "$config_file"
        echo "substitutions:" >> "$config_file"
        echo "  _SERVICE_NAME: '$service'" >> "$config_file"
    fi
    
    # Corriger les images avec substitutions
    sed -i "s|$CORRECT_REGISTRY/$service:|$CORRECT_REGISTRY/\${_SERVICE_NAME}:|g" "$config_file"
    
    echo -e "${GREEN}✅ $service corrigé${NC}"
}

# Correction de tous les services
for service in "${SERVICES[@]}"; do
    fix_cloudbuild_config "$service"
done

echo -e "${GREEN}=== Correction terminée ===${NC}"

# Validation
echo -e "${BLUE}=== Validation des corrections ===${NC}"
for service in "${SERVICES[@]}"; do
    config_file="apps/backend/$service/cloudbuild.yaml"
    if [ -f "$config_file" ]; then
        if grep -q "internal-and-cloud-load-balancing" "$config_file" && 
           grep -q "skillforge-ai-registry" "$config_file"; then
            echo -e "${GREEN}✅ $service: Configuration correcte${NC}"
        else
            echo -e "${RED}❌ $service: Problème de configuration${NC}"
        fi
    fi
done

echo -e "${GREEN}=== Script terminé ===${NC}"