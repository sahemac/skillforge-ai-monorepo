#!/bin/bash

# Commandes de déploiement par batch - optimisées pour exécution parallèle
# Utilisation: bash batch-deploy-commands.sh [BATCH_NUMBER]

set -e

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Fonction pour déployer un service en arrière-plan
deploy_service_async() {
    local service=$1
    local batch_name=$2
    
    echo -e "${BLUE}🚀 Démarrage build: $service${NC}"
    
    (
        cd "apps/backend/$service"
        echo "$(date): Début build $service" > "../../../logs/build_${service}.log"
        
        gcloud builds submit \
            --config cloudbuild.yaml \
            --timeout=1800s \
            --substitutions=_SERVICE_NAME=$service \
            --async \
            --format="value(metadata.build.id)" \
            >> "../../../logs/build_${service}.log" 2>&1
        
        local build_id=$(tail -1 "../../../logs/build_${service}.log")
        echo "Build ID: $build_id" >> "../../../logs/build_${service}.log"
        
        # Monitoring du build
        while true; do
            local status=$(gcloud builds describe "$build_id" --format="value(status)" 2>/dev/null || echo "UNKNOWN")
            
            case $status in
                "SUCCESS")
                    echo "$(date): Build $service SUCCÈS" >> "../../../logs/build_${service}.log"
                    echo -e "${GREEN}✅ $service: Build réussi${NC}"
                    break
                    ;;
                "FAILURE"|"TIMEOUT"|"CANCELLED")
                    echo "$(date): Build $service ÉCHEC ($status)" >> "../../../logs/build_${service}.log"
                    echo -e "${RED}❌ $service: Build échoué ($status)${NC}"
                    exit 1
                    ;;
                "WORKING"|"QUEUED")
                    echo "$(date): Build $service en cours..." >> "../../../logs/build_${service}.log"
                    sleep 30
                    ;;
                *)
                    echo "$(date): Build $service statut inconnu: $status" >> "../../../logs/build_${service}.log"
                    sleep 30
                    ;;
            esac
        done
    ) &
    
    return $!
}

# BATCH 1 - SERVICES CRITIQUES CORE
deploy_batch_1() {
    echo -e "${YELLOW}=== BATCH 1: SERVICES CRITIQUES CORE ===${NC}"
    
    local services=("subscription-service" "payment-service" "notification-service" "storage-service")
    local pids=()
    
    for service in "${services[@]}"; do
        deploy_service_async "$service" "BATCH_1"
        pids+=($!)
    done
    
    wait_and_validate_batch "BATCH_1" "${services[@]}"
}

# BATCH 2 - SERVICES FONCTIONNELS
deploy_batch_2() {
    echo -e "${YELLOW}=== BATCH 2: SERVICES FONCTIONNELS ===${NC}"
    
    local services=("content-service" "search-service" "project-service" "audit-service")
    local pids=()
    
    for service in "${services[@]}"; do
        deploy_service_async "$service" "BATCH_2"
        pids+=($!)
    done
    
    wait_and_validate_batch "BATCH_2" "${services[@]}"
}

# BATCH 3 - SERVICES AVANCÉS
deploy_batch_3() {
    echo -e "${YELLOW}=== BATCH 3: SERVICES AVANCÉS ===${NC}"
    
    local services=("matching-service" "workflow-service" "portfolio-service" "evaluation-service")
    local pids=()
    
    for service in "${services[@]}"; do
        deploy_service_async "$service" "BATCH_3"
        pids+=($!)
    done
    
    wait_and_validate_batch "BATCH_3" "${services[@]}"
}

# BATCH 4 - SERVICES COMMUNICATION
deploy_batch_4() {
    echo -e "${YELLOW}=== BATCH 4: SERVICES COMMUNICATION ===${NC}"
    
    local services=("chat-messaging-service" "realtime-collaboration-service" "scheduling-service")
    local pids=()
    
    for service in "${services[@]}"; do
        deploy_service_async "$service" "BATCH_4"
        pids+=($!)
    done
    
    wait_and_validate_batch "BATCH_4" "${services[@]}"
}

# BATCH 5 - SERVICES INTELLIGENCE
deploy_batch_5() {
    echo -e "${YELLOW}=== BATCH 5: SERVICES INTELLIGENCE ===${NC}"
    
    local services=("recommendation-service" "ai-orchestrator-service" "gamification-service" "localization-service" "integration-service")
    local pids=()
    
    for service in "${services[@]}"; do
        deploy_service_async "$service" "BATCH_5"
        pids+=($!)
    done
    
    wait_and_validate_batch "BATCH_5" "${services[@]}"
}

# Fonction d'attente et validation
wait_and_validate_batch() {
    local batch_name=$1
    shift
    local services=("$@")
    
    echo -e "${BLUE}⏳ Attente fin du $batch_name...${NC}"
    wait
    
    # Validation post-déploiement
    local failed_services=()
    for service in "${services[@]}"; do
        if validate_service_health "$service"; then
            echo -e "${GREEN}✅ $service: Validation réussie${NC}"
        else
            failed_services+=("$service")
            echo -e "${RED}❌ $service: Validation échouée${NC}"
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        echo -e "${GREEN}🎉 $batch_name: SUCCÈS COMPLET${NC}"
    else
        echo -e "${RED}💥 $batch_name: ÉCHECS DÉTECTÉS${NC}"
        echo "Services en échec: ${failed_services[*]}"
        exit 1
    fi
}

# Validation de santé d'un service
validate_service_health() {
    local service=$1
    
    # Vérifier que le service existe
    local service_url=$(gcloud run services describe "$service" \
        --region=$REGION \
        --format="value(status.url)" 2>/dev/null || echo "")
    
    if [ -z "$service_url" ]; then
        echo "Service $service non déployé"
        return 1
    fi
    
    # Test de santé HTTP
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" \
        "$service_url/health" 2>/dev/null || echo "000")
    
    if [ "$http_status" = "200" ]; then
        return 0
    else
        echo "Health check failed: $http_status"
        return 1
    fi
}

# Création des dossiers de logs
mkdir -p logs

# Sélection du batch à déployer
case "${1:-all}" in
    "1")
        deploy_batch_1
        ;;
    "2")
        deploy_batch_2
        ;;
    "3")
        deploy_batch_3
        ;;
    "4")
        deploy_batch_4
        ;;
    "5")
        deploy_batch_5
        ;;
    "all")
        echo -e "${BLUE}=== DÉPLOIEMENT MASSIF COMPLET ===${NC}"
        deploy_batch_1
        echo -e "${YELLOW}⏸️  Pause inter-batch (30s)${NC}"
        sleep 30
        
        deploy_batch_2
        echo -e "${YELLOW}⏸️  Pause inter-batch (30s)${NC}"
        sleep 30
        
        deploy_batch_3
        echo -e "${YELLOW}⏸️  Pause inter-batch (30s)${NC}"
        sleep 30
        
        deploy_batch_4
        echo -e "${YELLOW}⏸️  Pause inter-batch (30s)${NC}"
        sleep 30
        
        deploy_batch_5
        
        echo -e "${GREEN}🏁 DÉPLOIEMENT MASSIF TERMINÉ${NC}"
        ;;
    *)
        echo "Usage: $0 [1|2|3|4|5|all]"
        echo "  1 - Services critiques core"
        echo "  2 - Services fonctionnels"
        echo "  3 - Services avancés"
        echo "  4 - Services communication"
        echo "  5 - Services intelligence"
        echo "  all - Tous les batches en séquence"
        exit 1
        ;;
esac