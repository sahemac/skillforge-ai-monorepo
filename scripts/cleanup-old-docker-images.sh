#!/bin/bash

# Script de nettoyage des anciennes images Docker
# Supprime les services frontend obsolètes migrés vers le monolithe

set -e

PROJECT_ID="skillforge-ai-mvp-25"
REPO_NAME="skillforge-docker-repo"
REGION="europe-west1"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================================="
echo "NETTOYAGE DES IMAGES DOCKER OBSOLÈTES"
echo "=================================================="
echo ""

# Mode d'exécution
DRY_RUN=${1:-"--dry-run"}

if [ "$DRY_RUN" == "--execute" ]; then
  echo -e "${RED}⚠️  MODE EXÉCUTION: Les images seront DÉFINITIVEMENT supprimées${NC}"
  echo ""
  read -p "Êtes-vous sûr de vouloir continuer? (oui/non): " confirm
  if [ "$confirm" != "oui" ]; then
    echo "Opération annulée."
    exit 0
  fi
else
  echo -e "${YELLOW}MODE DRY-RUN: Aucune suppression ne sera effectuée${NC}"
  echo -e "${YELLOW}Lancez avec --execute pour supprimer réellement${NC}"
  echo ""
fi

# Services frontend obsolètes (migrés vers shell monolithe)
OBSOLETE_SERVICES=(
  "auth-service-staging"
  "learner-service-staging"
  "company-service-staging"
  "admin-service-staging"
)

echo "=================================================="
echo "1. SERVICES À SUPPRIMER"
echo "=================================================="
echo ""

total_space_freed=0

for service in "${OBSOLETE_SERVICES[@]}"; do
  echo ""
  echo -e "${BLUE}=== ${service} ===${NC}"

  # Vérifier si le service existe
  if gcloud artifacts docker images list ${REGISTRY}/${service} --include-tags 2>/dev/null | grep -q "${service}"; then

    # Lister les images
    echo ""
    echo "Images à supprimer:"
    gcloud artifacts docker images list ${REGISTRY}/${service} \
      --include-tags \
      --format="table(version,IMAGE_SIZE,createTime.date('%Y-%m-%d %H:%M'))" \
      --sort-by=~createTime

    # Calculer la taille si jq est disponible
    if command -v jq &> /dev/null; then
      service_size=$(gcloud artifacts docker images list ${REGISTRY}/${service} \
        --include-tags \
        --format=json | \
        jq -r '.[].sizeBytes // 0' | \
        awk '{sum+=$1} END {print sum}')

      service_gb=$(echo "scale=2; $service_size / 1073741824" | bc 2>/dev/null || echo "N/A")
      echo ""
      echo -e "${YELLOW}Espace à libérer:${NC} ${service_gb} GB"

      total_space_freed=$((total_space_freed + service_size))
    fi

    # Suppression
    if [ "$DRY_RUN" == "--execute" ]; then
      echo ""
      echo -e "${RED}Suppression en cours...${NC}"
      gcloud artifacts docker images delete ${REGISTRY}/${service} \
        --delete-tags --quiet && \
        echo -e "${GREEN}✓ Service ${service} supprimé${NC}" || \
        echo -e "${RED}✗ Erreur lors de la suppression de ${service}${NC}"
    else
      echo ""
      echo -e "${YELLOW}[DRY-RUN] Commande qui serait exécutée:${NC}"
      echo "gcloud artifacts docker images delete ${REGISTRY}/${service} --delete-tags --quiet"
    fi

  else
    echo -e "${GREEN}✓ Service déjà supprimé ou n'existe pas${NC}"
  fi
done

echo ""
echo "=================================================="
echo "2. NETTOYAGE DES IMAGES NON TAGUÉES (DANGLING)"
echo "=================================================="
echo ""

echo "Recherche des images sans tag (digest uniquement)..."
echo ""

# Note: Cette partie nécessite une logique plus complexe
# Les images sans tag apparaissent comme <none>:<none>
echo -e "${YELLOW}Pour nettoyer les images non taguées, utilisez:${NC}"
echo "gcloud artifacts docker images list ${REGISTRY} --filter='NOT tags:*' --format='get(version)'"
echo ""

if [ "$DRY_RUN" == "--execute" ]; then
  echo "Recherche et suppression des images non taguées..."

  # Liste des services actifs à vérifier
  ACTIVE_SERVICES=(
    "shell-service-staging"
    "user-service-staging"
  )

  for service in "${ACTIVE_SERVICES[@]}"; do
    echo ""
    echo -e "${BLUE}Vérification de ${service}...${NC}"

    # Lister toutes les versions
    versions=$(gcloud artifacts docker images list ${REGISTRY}/${service} \
      --format='get(version)' 2>/dev/null || echo "")

    if [ ! -z "$versions" ]; then
      # Garder les 3 dernières versions
      old_versions=$(echo "$versions" | tail -n +4)

      if [ ! -z "$old_versions" ]; then
        echo "Anciennes versions à supprimer (gardant les 3 plus récentes):"
        echo "$old_versions"

        for version in $old_versions; do
          echo -e "${RED}Suppression de ${service}:${version}${NC}"
          gcloud artifacts docker images delete \
            ${REGISTRY}/${service}@${version} \
            --quiet 2>/dev/null || echo "  Déjà supprimé"
        done
      else
        echo -e "${GREEN}✓ Moins de 3 versions, rien à supprimer${NC}"
      fi
    fi
  done
else
  echo -e "${YELLOW}[DRY-RUN] Mode simulation activé${NC}"
fi

echo ""
echo "=================================================="
echo "3. RÉSUMÉ"
echo "=================================================="
echo ""

if command -v jq &> /dev/null && [ $total_space_freed -gt 0 ]; then
  total_freed_gb=$(echo "scale=2; $total_space_freed / 1073741824" | bc)
  echo -e "${GREEN}Espace total libéré:${NC} ${total_freed_gb} GB"
else
  echo "Calcul de l'espace nécessite 'jq'"
fi

echo ""

if [ "$DRY_RUN" == "--execute" ]; then
  echo -e "${GREEN}✓ Nettoyage terminé${NC}"
else
  echo -e "${YELLOW}Pour exécuter réellement le nettoyage:${NC}"
  echo "./scripts/cleanup-old-docker-images.sh --execute"
fi

echo ""
echo "=================================================="
echo "4. PROCHAINES ÉTAPES RECOMMANDÉES"
echo "=================================================="
echo ""
echo "1. Vérifier les images restantes:"
echo "   gcloud artifacts docker images list ${REGISTRY}"
echo ""
echo "2. Construire et pousser la nouvelle image monolithique:"
echo "   cd apps/frontend/shell"
echo "   docker build -t ${REGISTRY}/shell-service-staging:latest ."
echo "   docker push ${REGISTRY}/shell-service-staging:latest"
echo ""
echo "3. Déployer sur Cloud Run:"
echo "   gcloud run deploy shell-service-staging \\"
echo "     --image ${REGISTRY}/shell-service-staging:latest \\"
echo "     --region ${REGION}"
echo ""
