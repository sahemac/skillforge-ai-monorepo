#!/bin/bash

# Script de monitoring et validation avancé pour les déploiements SkillForge AI
# Surveillance en temps réel des builds et services déployés

set -e

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
MONITORING_INTERVAL=30
MAX_RETRIES=3
HEALTH_TIMEOUT=10

echo -e "${BLUE}=== SkillForge AI - Monitoring & Validation ===${NC}"
echo "Project: $PROJECT_ID | Region: $REGION"
echo "Monitoring interval: ${MONITORING_INTERVAL}s"
echo ""

# Services attendus par batch
declare -A BATCH_SERVICES
BATCH_SERVICES[1]="subscription-service payment-service notification-service storage-service"
BATCH_SERVICES[2]="content-service search-service project-service audit-service"
BATCH_SERVICES[3]="matching-service workflow-service portfolio-service evaluation-service"
BATCH_SERVICES[4]="chat-messaging-service realtime-collaboration-service scheduling-service"
BATCH_SERVICES[5]="recommendation-service ai-orchestrator-service gamification-service localization-service integration-service"

# Fonction de monitoring en temps réel
monitor_active_builds() {
    echo -e "${CYAN}🔍 Monitoring des builds actifs${NC}"
    
    local active_builds=$(gcloud builds list \
        --ongoing \
        --format="table(id,substitutions.list(show='_SERVICE_NAME'),status,createTime.date(tz=LOCAL))" \
        --filter="substitutions._SERVICE_NAME:*-service" 2>/dev/null || echo "")
    
    if [ -n "$active_builds" ]; then
        echo "$active_builds"
    else
        echo "Aucun build actif détecté"
    fi
    echo ""
}

# Validation complète d'un service
validate_service_complete() {
    local service=$1
    local retries=0
    
    echo -e "${YELLOW}🔍 Validation complète: $service${NC}"
    
    while [ $retries -lt $MAX_RETRIES ]; do
        # 1. Vérifier existence du service
        local service_info=$(gcloud run services describe "$service" \
            --region=$REGION \
            --format="json" 2>/dev/null || echo "{}")
        
        if [ "$service_info" = "{}" ]; then
            echo -e "${RED}❌ Service $service non trouvé${NC}"
            ((retries++))
            sleep $MONITORING_INTERVAL
            continue
        fi
        
        # 2. Vérifier le statut du service
        local ready_status=$(echo "$service_info" | jq -r '.status.conditions[] | select(.type=="Ready") | .status // "Unknown"')
        local service_url=$(echo "$service_info" | jq -r '.status.url // ""')
        
        if [ "$ready_status" != "True" ]; then
            echo -e "${YELLOW}⚠️  Service $service pas encore prêt (status: $ready_status)${NC}"
            ((retries++))
            sleep $MONITORING_INTERVAL
            continue
        fi
        
        # 3. Vérifier les settings de configuration
        local ingress_setting=$(echo "$service_info" | jq -r '.spec.template.metadata.annotations["run.googleapis.com/ingress"] // "all"')
        local cpu_setting=$(echo "$service_info" | jq -r '.spec.template.spec.template.spec.containers[0].resources.limits.cpu // "unknown"')
        local memory_setting=$(echo "$service_info" | jq -r '.spec.template.spec.template.spec.containers[0].resources.limits.memory // "unknown"')
        
        echo -e "${BLUE}📋 Configuration $service:${NC}"
        echo "  URL: $service_url"
        echo "  Ingress: $ingress_setting"
        echo "  CPU: $cpu_setting"
        echo "  Memory: $memory_setting"
        
        # 4. Test de santé HTTP
        if [ -n "$service_url" ]; then
            echo -e "${CYAN}🏥 Test de santé HTTP${NC}"
            
            # Test endpoint /health
            local health_status=$(timeout $HEALTH_TIMEOUT curl -s -o /dev/null -w "%{http_code}" \
                "$service_url/health" 2>/dev/null || echo "000")
            
            # Test endpoint root
            local root_status=$(timeout $HEALTH_TIMEOUT curl -s -o /dev/null -w "%{http_code}" \
                "$service_url/" 2>/dev/null || echo "000")
            
            echo "  /health: $health_status"
            echo "  /: $root_status"
            
            if [ "$health_status" = "200" ] || [ "$root_status" = "200" ]; then
                echo -e "${GREEN}✅ $service: HTTP OK${NC}"
            else
                echo -e "${YELLOW}⚠️  $service: HTTP problématique${NC}"
            fi
        fi
        
        # 5. Vérifier les logs récents
        echo -e "${CYAN}📝 Logs récents${NC}"
        local recent_logs=$(gcloud logging read \
            "resource.type=cloud_run_revision AND resource.labels.service_name=$service" \
            --limit=5 \
            --format="value(timestamp,severity,textPayload)" \
            2>/dev/null || echo "")
        
        if [ -n "$recent_logs" ]; then
            echo "$recent_logs" | head -3
        else
            echo "  Pas de logs récents trouvés"
        fi
        
        # 6. Validation finale
        if [ "$ready_status" = "True" ] && [ "$ingress_setting" = "internal-and-cloud-load-balancing" ]; then
            echo -e "${GREEN}✅ $service: VALIDATION COMPLÈTE${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  $service: Configuration à corriger${NC}"
            if [ "$ingress_setting" != "internal-and-cloud-load-balancing" ]; then
                fix_service_ingress "$service"
            fi
            return 1
        fi
    done
    
    echo -e "${RED}❌ $service: Validation échouée après $MAX_RETRIES tentatives${NC}"
    return 1
}

# Correction automatique des settings ingress
fix_service_ingress() {
    local service=$1
    
    echo -e "${YELLOW}🔧 Correction ingress: $service${NC}"
    
    gcloud run services update "$service" \
        --region=$REGION \
        --ingress=internal-and-cloud-load-balancing \
        --quiet \
        && echo -e "${GREEN}✅ Ingress corrigé pour $service${NC}" \
        || echo -e "${RED}❌ Échec correction ingress pour $service${NC}"
}

# Dashboard de statut en temps réel
show_deployment_dashboard() {
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}     ${BLUE}SkillForge AI - Dashboard Déploiement${NC}     ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Status global
    local total_services=0
    local ready_services=0
    local failed_services=0
    
    echo -e "${BLUE}📊 STATUT GLOBAL${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Analyser chaque batch
    for batch in {1..5}; do
        echo -e "${CYAN}📦 BATCH $batch${NC}"
        
        local services=(${BATCH_SERVICES[$batch]})
        local batch_ready=0
        local batch_total=${#services[@]}
        
        for service in "${services[@]}"; do
            ((total_services++))
            
            local status=$(gcloud run services describe "$service" \
                --region=$REGION \
                --format="value(status.conditions[0].status)" 2>/dev/null || echo "Missing")
            
            case $status in
                "True")
                    echo -e "  ${GREEN}✅ $service${NC}"
                    ((ready_services++))
                    ((batch_ready++))
                    ;;
                "False")
                    echo -e "  ${RED}❌ $service${NC}"
                    ((failed_services++))
                    ;;
                "Unknown")
                    echo -e "  ${YELLOW}⏳ $service${NC}"
                    ;;
                "Missing")
                    echo -e "  ${RED}🚫 $service (non déployé)${NC}"
                    ((failed_services++))
                    ;;
                *)
                    echo -e "  ${YELLOW}❓ $service ($status)${NC}"
                    ;;
            esac
        done
        
        echo -e "  ${BLUE}Progress: $batch_ready/$batch_total${NC}"
        echo ""
    done
    
    # Statistiques finales
    echo -e "${PURPLE}📈 RÉSUMÉ${NC}"
    echo -e "Total: $total_services | ${GREEN}Prêts: $ready_services${NC} | ${RED}Échecs: $failed_services${NC}"
    echo -e "Taux de réussite: $(( ready_services * 100 / total_services ))%"
    echo ""
}

# Commandes utilitaires
case "${1:-monitor}" in
    "monitor")
        echo -e "${BLUE}🚀 Démarrage monitoring continu${NC}"
        while true; do
            show_deployment_dashboard
            monitor_active_builds
            sleep $MONITORING_INTERVAL
        done
        ;;
    
    "validate")
        echo -e "${BLUE}🔍 Validation complète de tous les services${NC}"
        failed_count=0
        
        for batch in {1..5}; do
            services=(${BATCH_SERVICES[$batch]})
            echo -e "${CYAN}=== VALIDATION BATCH $batch ===${NC}"
            
            for service in "${services[@]}"; do
                if ! validate_service_complete "$service"; then
                    ((failed_count++))
                fi
                echo ""
            done
        done
        
        if [ $failed_count -eq 0 ]; then
            echo -e "${GREEN}🎉 VALIDATION GLOBALE RÉUSSIE${NC}"
        else
            echo -e "${RED}💥 $failed_count services ont des problèmes${NC}"
        fi
        ;;
    
    "dashboard")
        show_deployment_dashboard
        ;;
    
    "fix-ingress")
        echo -e "${YELLOW}🔧 Correction des settings ingress${NC}"
        for batch in {1..5}; do
            services=(${BATCH_SERVICES[$batch]})
            for service in "${services[@]}"; do
                fix_service_ingress "$service"
            done
        done
        ;;
    
    "health-check")
        service_name="$2"
        if [ -z "$service_name" ]; then
            echo "Usage: $0 health-check <service-name>"
            exit 1
        fi
        validate_service_complete "$service_name"
        ;;
    
    *)
        echo "Usage: $0 [monitor|validate|dashboard|fix-ingress|health-check]"
        echo "  monitor      - Monitoring continu avec dashboard"
        echo "  validate     - Validation complète de tous les services"
        echo "  dashboard    - Affichage du dashboard une fois"
        echo "  fix-ingress  - Correction des settings ingress"
        echo "  health-check - Test de santé d'un service spécifique"
        exit 1
        ;;
esac