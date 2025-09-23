#!/bin/bash

# SkillForge AI - Stratégie de Déploiement Massif Backend Services
# Script de déploiement optimisé par batches avec gestion des dépendances

set -e

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"
REGISTRY="europe-west1-docker.pkg.dev/$PROJECT_ID/skillforge-ai-registry"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== SkillForge AI - Déploiement Massif Backend ===${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Registry: $REGISTRY"
echo ""

# BATCH 1 - SERVICES CRITIQUES CORE (dépendances minimales)
BATCH_1=(
    "subscription-service"
    "payment-service" 
    "notification-service"
    "storage-service"
)

# BATCH 2 - SERVICES FONCTIONNELS (dépendent du batch 1)
BATCH_2=(
    "content-service"
    "search-service"
    "project-service"
    "audit-service"
)

# BATCH 3 - SERVICES AVANCÉS (dépendent des batches 1&2)
BATCH_3=(
    "matching-service"
    "workflow-service"
    "portfolio-service"
    "evaluation-service"
)

# BATCH 4 - SERVICES COMMUNICATION (peuvent fonctionner indépendamment)
BATCH_4=(
    "chat-messaging-service"
    "realtime-collaboration-service"
    "scheduling-service"
)

# BATCH 5 - SERVICES INTELLIGENCE (dépendent de tous les autres)
BATCH_5=(
    "recommendation-service"
    "ai-orchestrator-service"
    "gamification-service"
    "localization-service"
    "integration-service"
)

# Fonction de build parallèle pour un batch
deploy_batch() {
    local batch_name=$1
    shift
    local services=("$@")
    
    echo -e "${YELLOW}=== DÉBUT BATCH $batch_name ===${NC}"
    echo "Services: ${services[*]}"
    echo ""
    
    # Démarrer tous les builds en parallèle
    local pids=()
    for service in "${services[@]}"; do
        echo -e "${BLUE}Démarrage build: $service${NC}"
        (
            cd "apps/backend/$service"
            gcloud builds submit --config cloudbuild.yaml --timeout=1800s \
                --substitutions=_SERVICE_NAME=$service,_REGISTRY_URL=$REGISTRY \
                > "../../../logs/build_${service}.log" 2>&1
            echo "Build $service terminé avec code: $?"
        ) &
        pids+=($!)
    done
    
    # Attendre tous les builds du batch
    local failed_services=()
    for i in "${!pids[@]}"; do
        wait ${pids[$i]}
        local exit_code=$?
        if [ $exit_code -ne 0 ]; then
            failed_services+=("${services[$i]}")
            echo -e "${RED}ÉCHEC: ${services[$i]}${NC}"
        else
            echo -e "${GREEN}SUCCÈS: ${services[$i]}${NC}"
        fi
    done
    
    # Vérification post-déploiement
    for service in "${services[@]}"; do
        if [[ ! " ${failed_services[@]} " =~ " ${service} " ]]; then
            validate_service_deployment "$service"
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        echo -e "${GREEN}=== BATCH $batch_name TERMINÉ AVEC SUCCÈS ===${NC}"
    else
        echo -e "${RED}=== BATCH $batch_name TERMINÉ AVEC ÉCHECS ===${NC}"
        echo "Services en échec: ${failed_services[*]}"
        exit 1
    fi
    echo ""
}

# Validation d'un service déployé
validate_service_deployment() {
    local service=$1
    local service_url
    
    echo -e "${BLUE}Validation: $service${NC}"
    
    # Récupérer l'URL du service
    service_url=$(gcloud run services describe "$service" \
        --region=$REGION \
        --format="value(status.url)" 2>/dev/null || echo "")
    
    if [ -z "$service_url" ]; then
        echo -e "${RED}❌ Service $service non trouvé${NC}"
        return 1
    fi
    
    # Test de santé
    local health_status
    health_status=$(curl -s -o /dev/null -w "%{http_code}" "$service_url/health" 2>/dev/null || echo "000")
    
    if [ "$health_status" = "200" ]; then
        echo -e "${GREEN}✅ $service: Health check OK${NC}"
    else
        echo -e "${YELLOW}⚠️  $service: Health check failed ($health_status)${NC}"
    fi
    
    # Vérifier les settings ingress
    local ingress_setting
    ingress_setting=$(gcloud run services describe "$service" \
        --region=$REGION \
        --format="value(spec.template.metadata.annotations['run.googleapis.com/ingress'])" 2>/dev/null || echo "")
    
    if [ "$ingress_setting" = "internal-and-cloud-load-balancing" ]; then
        echo -e "${GREEN}✅ $service: Ingress settings correct${NC}"
    else
        echo -e "${RED}❌ $service: Ingress incorrect ($ingress_setting)${NC}"
        fix_ingress_setting "$service"
    fi
}

# Correction des settings ingress
fix_ingress_setting() {
    local service=$1
    echo -e "${YELLOW}Correction ingress pour $service${NC}"
    
    gcloud run services update "$service" \
        --region=$REGION \
        --ingress=internal-and-cloud-load-balancing \
        --quiet
    
    echo -e "${GREEN}✅ Ingress corrigé pour $service${NC}"
}

# Création des dossiers de logs
mkdir -p logs

# Pré-vérifications
echo -e "${YELLOW}=== PRÉ-VÉRIFICATIONS ===${NC}"

# Vérifier l'authentification GCP
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${RED}❌ Pas d'authentification GCP active${NC}"
    exit 1
fi

# Vérifier le projet
if [ "$(gcloud config get-value project)" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Configuration du projet...${NC}"
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}✅ Pré-vérifications OK${NC}"
echo ""

# Exécution des batches
echo -e "${BLUE}=== DÉBUT DÉPLOIEMENT MASSIF ===${NC}"
echo "Timestamp: $(date)"
echo ""

deploy_batch "1-CRITIQUES" "${BATCH_1[@]}"
sleep 30  # Pause entre batches

deploy_batch "2-FONCTIONNELS" "${BATCH_2[@]}"
sleep 30

deploy_batch "3-AVANCÉS" "${BATCH_3[@]}"
sleep 30

deploy_batch "4-COMMUNICATION" "${BATCH_4[@]}"
sleep 30

deploy_batch "5-INTELLIGENCE" "${BATCH_5[@]}"

echo -e "${GREEN}=== DÉPLOIEMENT MASSIF TERMINÉ ===${NC}"
echo "Timestamp: $(date)"
echo ""

# Récapitulatif final
echo -e "${BLUE}=== RÉCAPITULATIF FINAL ===${NC}"
gcloud run services list --region=$REGION --format="table(metadata.name,status.url,status.conditions[0].status)"

echo -e "${GREEN}=== DÉPLOIEMENT MASSIF COMPLÉTÉ ===${NC}"