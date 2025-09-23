#!/bin/bash

# Script de correction massive des settings ingress pour tous les services SkillForge AI
# Corrige l'ingress de "all" vers "internal-and-cloud-load-balancing" pour la sécurité

set -e

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=== Correction Massive des Settings Ingress ===${NC}"
echo "Project: $PROJECT_ID | Region: $REGION"
echo "Target: internal-and-cloud-load-balancing"
echo ""

# Liste complète des services backend à corriger
ALL_SERVICES=(
    # Services déjà déployés
    "user-service-staging"
    "company-service"
    "analytics-service"
    
    # Services à déployer - Batch 1
    "subscription-service"
    "payment-service"
    "notification-service"
    "storage-service"
    
    # Services à déployer - Batch 2
    "content-service"
    "search-service"
    "project-service"
    "audit-service"
    
    # Services à déployer - Batch 3
    "matching-service"
    "workflow-service"
    "portfolio-service"
    "evaluation-service"
    
    # Services à déployer - Batch 4
    "chat-messaging-service"
    "realtime-collaboration-service"
    "scheduling-service"
    
    # Services à déployer - Batch 5
    "recommendation-service"
    "ai-orchestrator-service"
    "gamification-service"
    "localization-service"
    "integration-service"
)

# Fonction de vérification du statut ingress actuel
check_ingress_status() {
    local service=$1
    
    local ingress_setting=$(gcloud run services describe "$service" \
        --region=$REGION \
        --format="value(spec.template.metadata.annotations['run.googleapis.com/ingress'])" 2>/dev/null || echo "not-found")
    
    echo "$ingress_setting"
}

# Fonction de correction d'un service
fix_service_ingress() {
    local service=$1
    local current_ingress=$2
    
    if [ "$current_ingress" = "not-found" ]; then
        echo -e "${RED}❌ $service: Service non trouvé${NC}"
        return 1
    fi
    
    if [ "$current_ingress" = "internal-and-cloud-load-balancing" ]; then
        echo -e "${GREEN}✅ $service: Déjà correct${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}🔧 $service: Correction $current_ingress → internal-and-cloud-load-balancing${NC}"
    
    # Tentative de correction
    if gcloud run services update "$service" \
        --region=$REGION \
        --ingress=internal-and-cloud-load-balancing \
        --quiet 2>/dev/null; then
        
        echo -e "${GREEN}✅ $service: Correction réussie${NC}"
        return 0
    else
        echo -e "${RED}❌ $service: Échec de la correction${NC}"
        return 1
    fi
}

# Fonction de correction en lot avec parallélisation
fix_batch_ingress() {
    local batch_name=$1
    shift
    local services=("$@")
    local pids=()
    local results=()
    
    echo -e "${CYAN}=== $batch_name ===${NC}"
    
    # Lancer les corrections en parallèle
    for service in "${services[@]}"; do
        (
            current_ingress=$(check_ingress_status "$service")
            fix_service_ingress "$service" "$current_ingress"
            echo $? > "/tmp/fix_result_${service}"
        ) &
        pids+=($!)
    done
    
    # Attendre la fin de toutes les corrections
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    # Collecter les résultats
    local success_count=0
    local failure_count=0
    
    for service in "${services[@]}"; do
        if [ -f "/tmp/fix_result_${service}" ]; then
            local result=$(cat "/tmp/fix_result_${service}")
            rm -f "/tmp/fix_result_${service}"
            
            if [ "$result" = "0" ]; then
                ((success_count++))
            else
                ((failure_count++))
            fi
        else
            ((failure_count++))
        fi
    done
    
    echo -e "${BLUE}📊 $batch_name: ${GREEN}$success_count réussies${NC}, ${RED}$failure_count échecs${NC}"
    echo ""
}

# Audit complet avant correction
echo -e "${CYAN}🔍 AUDIT INITIAL${NC}"
echo ""

existing_services=()
missing_services=()
correct_services=()
incorrect_services=()

for service in "${ALL_SERVICES[@]}"; do
    current_ingress=$(check_ingress_status "$service")
    
    if [ "$current_ingress" = "not-found" ]; then
        missing_services+=("$service")
        echo -e "${RED}🚫 $service: Non déployé${NC}"
    elif [ "$current_ingress" = "internal-and-cloud-load-balancing" ]; then
        existing_services+=("$service")
        correct_services+=("$service")
        echo -e "${GREEN}✅ $service: Correct${NC}"
    else
        existing_services+=("$service")
        incorrect_services+=("$service")
        echo -e "${YELLOW}⚠️  $service: $current_ingress (à corriger)${NC}"
    fi
done

echo ""
echo -e "${BLUE}📈 STATISTIQUES INITIALES${NC}"
echo "Total services: ${#ALL_SERVICES[@]}"
echo "Déployés: ${#existing_services[@]}"
echo "Non déployés: ${#missing_services[@]}"
echo "Correctement configurés: ${#correct_services[@]}"
echo "À corriger: ${#incorrect_services[@]}"
echo ""

# Correction des services existants incorrects
if [ ${#incorrect_services[@]} -gt 0 ]; then
    echo -e "${YELLOW}🔧 CORRECTION DES SERVICES INCORRECTS${NC}"
    
    # Diviser en lots pour éviter la surcharge
    batch_size=5
    batch_num=1
    
    for ((i=0; i<${#incorrect_services[@]}; i+=batch_size)); do
        batch_services=("${incorrect_services[@]:i:batch_size}")
        fix_batch_ingress "BATCH $batch_num" "${batch_services[@]}"
        ((batch_num++))
        
        # Pause entre les lots
        if [ $i -lt $((${#incorrect_services[@]} - batch_size)) ]; then
            echo -e "${BLUE}⏸️  Pause inter-batch (10s)${NC}"
            sleep 10
        fi
    done
else
    echo -e "${GREEN}🎉 Tous les services déployés sont déjà correctement configurés${NC}"
fi

# Audit final
echo -e "${CYAN}🔍 AUDIT FINAL${NC}"
echo ""

final_correct=0
final_incorrect=0

for service in "${existing_services[@]}"; do
    current_ingress=$(check_ingress_status "$service")
    
    if [ "$current_ingress" = "internal-and-cloud-load-balancing" ]; then
        ((final_correct++))
        echo -e "${GREEN}✅ $service: Correct${NC}"
    else
        ((final_incorrect++))
        echo -e "${RED}❌ $service: Toujours incorrect ($current_ingress)${NC}"
    fi
done

echo ""
echo -e "${BLUE}📊 RÉSULTATS FINAUX${NC}"
echo "Services correctement configurés: $final_correct"
echo "Services encore incorrects: $final_incorrect"

if [ $final_incorrect -eq 0 ]; then
    echo -e "${GREEN}🎉 CORRECTION MASSIVE RÉUSSIE${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Certains services nécessitent une attention manuelle${NC}"
    exit 1
fi

# Commandes de vérification suggérées
echo ""
echo -e "${BLUE}🔧 COMMANDES DE VÉRIFICATION${NC}"
echo "Vérifier tous les services:"
echo "  gcloud run services list --region=$REGION --format=\"table(metadata.name,spec.template.metadata.annotations['run.googleapis.com/ingress'])\""
echo ""
echo "Monitoring continu:"
echo "  bash scripts/monitor-and-validate-deployments.sh monitor"