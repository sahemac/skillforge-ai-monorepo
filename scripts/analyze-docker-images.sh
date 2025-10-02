#!/bin/bash

# Script d'analyse et de nettoyage des images Docker sur Artifact Registry
# Ce script identifie les anciennes images et calcule les gains d'espace potentiels

set -e

PROJECT_ID="skillforge-ai-mvp-25"
REPO_NAME="skillforge-docker-repo"
REGION="europe-west1"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

echo "=================================================="
echo "ANALYSE DES IMAGES DOCKER - ARTIFACT REGISTRY"
echo "=================================================="
echo ""

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Projet:${NC} ${PROJECT_ID}"
echo -e "${BLUE}Repository:${NC} ${REPO_NAME}"
echo -e "${BLUE}Région:${NC} ${REGION}"
echo ""

# 1. Lister toutes les images avec leurs tailles
echo "=================================================="
echo "1. INVENTAIRE COMPLET DES IMAGES"
echo "=================================================="
echo ""

gcloud artifacts docker images list ${REGISTRY} \
  --include-tags \
  --format="table(
    package:label='SERVICE',
    version:label='TAG',
    IMAGE_SIZE:label='TAILLE',
    createTime.date('%Y-%m-%d %H:%M'):label='DATE_CREATION',
    updateTime.date('%Y-%m-%d %H:%M'):label='DERNIERE_MAJ'
  )" \
  --sort-by=~createTime

echo ""
echo "=================================================="
echo "2. ANALYSE PAR SERVICE (FRONTEND)"
echo "=================================================="
echo ""

# Services frontend à analyser
FRONTEND_SERVICES=(
  "shell-service-staging"
  "auth-service-staging"
  "learner-service-staging"
  "company-service-staging"
  "admin-service-staging"
  "documentation-service-staging"
)

for service in "${FRONTEND_SERVICES[@]}"; do
  echo ""
  echo -e "${YELLOW}=== ${service} ===${NC}"

  # Compter les images
  count=$(gcloud artifacts docker images list ${REGISTRY}/${service} --include-tags 2>/dev/null | wc -l)

  if [ $count -gt 1 ]; then
    echo -e "${GREEN}Nombre d'images:${NC} $((count - 1))"

    # Lister avec tailles
    gcloud artifacts docker images list ${REGISTRY}/${service} \
      --include-tags \
      --format="table(version,IMAGE_SIZE,createTime.date('%Y-%m-%d %H:%M'))" \
      --sort-by=~createTime 2>/dev/null || echo "Aucune image trouvée"
  else
    echo -e "${RED}Service non trouvé ou aucune image${NC}"
  fi
done

echo ""
echo "=================================================="
echo "3. RECOMMANDATIONS DE NETTOYAGE"
echo "=================================================="
echo ""

echo -e "${YELLOW}Stratégie recommandée:${NC}"
echo ""
echo "1. ${GREEN}CONSERVER:${NC}"
echo "   - Images avec tag 'latest'"
echo "   - Images créées dans les dernières 48h"
echo "   - Images actuellement déployées sur Cloud Run"
echo ""
echo "2. ${RED}SUPPRIMER:${NC}"
echo "   - Images sans tag (digest uniquement)"
echo "   - Images de plus de 7 jours non utilisées"
echo "   - Images de services obsolètes (auth, learner, company, admin individuels)"
echo ""
echo "3. ${BLUE}SERVICES OBSOLÈTES (À NETTOYER):${NC}"
echo "   - auth-service-staging → migré vers shell"
echo "   - learner-service-staging → migré vers shell"
echo "   - company-service-staging → migré vers shell"
echo "   - admin-service-staging → migré vers shell"
echo "   - documentation-service-staging → optionnel"
echo ""
echo "4. ${GREEN}NOUVELLE ARCHITECTURE:${NC}"
echo "   - shell-service-staging (MONOLITHE)"
echo ""

echo "=================================================="
echo "4. CALCUL DES GAINS POTENTIELS"
echo "=================================================="
echo ""

# Calculer l'espace total utilisé
echo "Calcul de l'espace total utilisé..."
echo ""

# Cette commande nécessite jq pour parser le JSON
if command -v jq &> /dev/null; then
  total_size=$(gcloud artifacts docker images list ${REGISTRY} \
    --include-tags \
    --format=json | \
    jq -r '.[].sizeBytes // 0' | \
    awk '{sum+=$1} END {print sum}')

  # Convertir en GB
  total_gb=$(echo "scale=2; $total_size / 1073741824" | bc)
  echo -e "${BLUE}Espace total utilisé:${NC} ${total_gb} GB"

  # Estimer l'espace libérable (anciennes images frontend)
  old_frontend_size=$(gcloud artifacts docker images list ${REGISTRY} \
    --include-tags \
    --format=json | \
    jq -r '.[] | select(.package | contains("auth-service") or contains("learner-service") or contains("company-service") or contains("admin-service")) | .sizeBytes // 0' | \
    awk '{sum+=$1} END {print sum}')

  old_frontend_gb=$(echo "scale=2; $old_frontend_size / 1073741824" | bc)

  echo -e "${RED}Espace libérable (services obsolètes):${NC} ${old_frontend_gb} GB"
  echo -e "${GREEN}Gain potentiel:${NC} $((old_frontend_size * 100 / total_size))%"
else
  echo -e "${YELLOW}⚠️  Installez 'jq' pour le calcul précis des tailles${NC}"
  echo "   sudo apt-get install jq (Linux)"
  echo "   brew install jq (macOS)"
fi

echo ""
echo "=================================================="
echo "5. COMMANDES DE NETTOYAGE"
echo "=================================================="
echo ""

echo "Pour supprimer une image spécifique:"
echo -e "${YELLOW}gcloud artifacts docker images delete ${REGISTRY}/SERVICE:TAG --quiet${NC}"
echo ""

echo "Pour supprimer toutes les images d'un service:"
echo -e "${YELLOW}gcloud artifacts docker images delete ${REGISTRY}/SERVICE --delete-tags --quiet${NC}"
echo ""

echo "Pour supprimer les services frontend obsolètes:"
cat << 'CLEANUP_SCRIPT'
# Services à supprimer (migré vers monolithe)
OBSOLETE_SERVICES=(
  "auth-service-staging"
  "learner-service-staging"
  "company-service-staging"
  "admin-service-staging"
)

for service in "${OBSOLETE_SERVICES[@]}"; do
  echo "Suppression de ${service}..."
  gcloud artifacts docker images delete \
    europe-west1-docker.pkg.dev/skillforge-ai-mvp-25/skillforge-docker-repo/${service} \
    --delete-tags --quiet || echo "Service ${service} déjà supprimé"
done
CLEANUP_SCRIPT

echo ""
echo -e "${GREEN}✓ Analyse terminée${NC}"
echo ""
