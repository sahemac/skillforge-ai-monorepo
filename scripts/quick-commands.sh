#!/bin/bash

# Script de commandes rapides pour le déploiement massif SkillForge AI
# Usage: bash scripts/quick-commands.sh [COMMAND]

PROJECT_ID="skillforge-ai-mvp-25"
REGION="europe-west1"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

case "${1:-help}" in
    "setup")
        echo -e "${BLUE}🔧 Configuration initiale${NC}"
        gcloud config set project $PROJECT_ID
        mkdir -p logs
        echo -e "${GREEN}✅ Configuration terminée${NC}"
        ;;
    
    "fix-configs")
        echo -e "${YELLOW}🔧 Correction des configurations cloudbuild.yaml${NC}"
        bash scripts/fix-cloudbuild-configs.sh
        ;;
    
    "deploy-all")
        echo -e "${BLUE}🚀 Déploiement complet de tous les batches${NC}"
        bash scripts/batch-deploy-commands.sh all
        ;;
    
    "deploy-1"|"deploy-2"|"deploy-3"|"deploy-4"|"deploy-5")
        batch_num=${1#deploy-}
        echo -e "${BLUE}🚀 Déploiement du batch $batch_num${NC}"
        bash scripts/batch-deploy-commands.sh $batch_num
        ;;
    
    "monitor")
        echo -e "${CYAN}📊 Monitoring en temps réel${NC}"
        bash scripts/monitor-and-validate-deployments.sh monitor
        ;;
    
    "validate")
        echo -e "${CYAN}✅ Validation complète${NC}"
        bash scripts/monitor-and-validate-deployments.sh validate
        ;;
    
    "dashboard")
        echo -e "${CYAN}📊 Dashboard statut${NC}"
        bash scripts/monitor-and-validate-deployments.sh dashboard
        ;;
    
    "fix-ingress")
        echo -e "${YELLOW}🔐 Correction settings ingress${NC}"
        bash scripts/fix-ingress-settings-massive.sh
        ;;
    
    "status")
        echo -e "${BLUE}📊 Statut des services${NC}"
        gcloud run services list --region=$REGION --format="table(metadata.name,status.url,status.conditions[0].status)"
        ;;
    
    "logs")
        service_name="$2"
        if [ -z "$service_name" ]; then
            echo "Usage: $0 logs <service-name>"
            exit 1
        fi
        echo -e "${CYAN}📝 Logs de $service_name${NC}"
        gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$service_name" --limit=50
        ;;
    
    "complete")
        echo -e "${BLUE}🎯 Déploiement complet automatisé${NC}"
        echo "1. Configuration..."
        gcloud config set project $PROJECT_ID
        mkdir -p logs
        
        echo "2. Correction des configurations..."
        bash scripts/fix-cloudbuild-configs.sh
        
        echo "3. Déploiement par batches..."
        bash scripts/batch-deploy-commands.sh all
        
        echo "4. Correction des ingress..."
        bash scripts/fix-ingress-settings-massive.sh
        
        echo "5. Validation finale..."
        bash scripts/monitor-and-validate-deployments.sh validate
        
        echo -e "${GREEN}🎉 Déploiement complet terminé${NC}"
        ;;
    
    "clean")
        echo -e "${YELLOW}🧹 Nettoyage des logs${NC}"
        rm -rf logs/*
        echo -e "${GREEN}✅ Logs nettoyés${NC}"
        ;;
    
    "test-service")
        service_name="$2"
        if [ -z "$service_name" ]; then
            echo "Usage: $0 test-service <service-name>"
            exit 1
        fi
        echo -e "${CYAN}🧪 Test de santé: $service_name${NC}"
        bash scripts/monitor-and-validate-deployments.sh health-check $service_name
        ;;
    
    "build-single")
        service_name="$2"
        if [ -z "$service_name" ]; then
            echo "Usage: $0 build-single <service-name>"
            exit 1
        fi
        echo -e "${BLUE}🏗️ Build individuel: $service_name${NC}"
        cd "apps/backend/$service_name"
        gcloud builds submit --config cloudbuild.yaml --substitutions=_SERVICE_NAME=$service_name
        ;;
    
    "list-builds")
        echo -e "${BLUE}📋 Builds en cours${NC}"
        gcloud builds list --ongoing --format="table(id,substitutions.list(show='_SERVICE_NAME'),status,createTime.date(tz=LOCAL))"
        ;;
    
    "help"|*)
        echo -e "${BLUE}🔧 Commandes rapides - Déploiement SkillForge AI${NC}"
        echo ""
        echo -e "${YELLOW}Configuration:${NC}"
        echo "  setup           - Configuration initiale du projet"
        echo "  fix-configs     - Corriger les configurations cloudbuild.yaml"
        echo ""
        echo -e "${YELLOW}Déploiement:${NC}"
        echo "  deploy-all      - Déployer tous les batches en séquence"
        echo "  deploy-1        - Déployer le batch 1 (services critiques)"
        echo "  deploy-2        - Déployer le batch 2 (services fonctionnels)"
        echo "  deploy-3        - Déployer le batch 3 (services avancés)"
        echo "  deploy-4        - Déployer le batch 4 (services communication)"
        echo "  deploy-5        - Déployer le batch 5 (services intelligence)"
        echo "  build-single <service> - Build d'un service spécifique"
        echo ""
        echo -e "${YELLOW}Monitoring:${NC}"
        echo "  monitor         - Dashboard de monitoring en temps réel"
        echo "  validate        - Validation complète de tous les services"
        echo "  dashboard       - Affichage du dashboard une fois"
        echo "  status          - Statut rapide de tous les services"
        echo "  list-builds     - Lister les builds en cours"
        echo ""
        echo -e "${YELLOW}Maintenance:${NC}"
        echo "  fix-ingress     - Corriger les settings ingress de sécurité"
        echo "  test-service <service> - Test de santé d'un service"
        echo "  logs <service>  - Afficher les logs d'un service"
        echo "  clean           - Nettoyer les logs locaux"
        echo ""
        echo -e "${YELLOW}Tout-en-un:${NC}"
        echo "  complete        - Déploiement complet automatisé"
        echo ""
        echo -e "${CYAN}Exemples:${NC}"
        echo "  bash scripts/quick-commands.sh setup"
        echo "  bash scripts/quick-commands.sh deploy-1"
        echo "  bash scripts/quick-commands.sh monitor"
        echo "  bash scripts/quick-commands.sh test-service subscription-service"
        echo "  bash scripts/quick-commands.sh complete"
        ;;
esac