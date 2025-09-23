#!/bin/bash

# Script de validation des configurations PostgreSQL pour SkillForge AI

echo "======================================="
echo "VALIDATION CONFIGURATION POSTGRESQL"
echo "======================================="
echo ""

# Configuration requise
REQUIRED_CONFIG="POSTGRES_HOST=127.0.0.1,POSTGRES_PORT=5432,POSTGRES_DB=skillforge_db,POSTGRES_USER=skillforge_user,POSTGRES_PASSWORD=Psaumes@27"

echo "Configuration PostgreSQL standardisée:"
echo "- POSTGRES_HOST=127.0.0.1"
echo "- POSTGRES_PORT=5432"
echo "- POSTGRES_DB=skillforge_db"
echo "- POSTGRES_USER=skillforge_user"
echo "- POSTGRES_PASSWORD=Psaumes@27"
echo "- DATABASE_URL=postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
echo ""

echo "=== ANALYSE DES SERVICES ==="
echo ""

# Compter les services
TOTAL_SERVICES=$(ls apps/backend/ | wc -l)
TOTAL_CLOUDBUILD=$(find apps/backend -name "cloudbuild.yaml" | wc -l)

echo "Services backend totaux: $TOTAL_SERVICES"
echo "Fichiers cloudbuild.yaml: $TOTAL_CLOUDBUILD"
echo ""

if [ "$TOTAL_SERVICES" -eq "$TOTAL_CLOUDBUILD" ]; then
    echo "✅ SUCCÈS: Tous les services ont un fichier cloudbuild.yaml"
else
    echo "❌ ERREUR: $(($TOTAL_SERVICES - $TOTAL_CLOUDBUILD)) services manquent cloudbuild.yaml"
    echo ""
    echo "Services sans cloudbuild.yaml:"
    for service in $(ls apps/backend/); do
        if [ ! -f "apps/backend/$service/cloudbuild.yaml" ]; then
            echo "  ❌ $service"
        fi
    done
fi
echo ""

echo "=== VALIDATION VARIABLES POSTGRESQL ==="
echo ""

# Vérifier les variables PostgreSQL
POSTGRES_HOST_COUNT=$(grep -c "POSTGRES_HOST=127.0.0.1" apps/backend/*/cloudbuild.yaml 2>/dev/null | wc -l)
POSTGRES_PORT_COUNT=$(grep -c "POSTGRES_PORT=5432" apps/backend/*/cloudbuild.yaml 2>/dev/null | wc -l)
POSTGRES_DB_COUNT=$(grep -c "POSTGRES_DB=skillforge_db" apps/backend/*/cloudbuild.yaml 2>/dev/null | wc -l)
POSTGRES_USER_COUNT=$(grep -c "POSTGRES_USER=skillforge_user" apps/backend/*/cloudbuild.yaml 2>/dev/null | wc -l)
POSTGRES_PASSWORD_COUNT=$(grep -c "POSTGRES_PASSWORD=Psaumes@27" apps/backend/*/cloudbuild.yaml 2>/dev/null | wc -l)
DATABASE_URL_COUNT=$(grep -c "DATABASE_URL=postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db" apps/backend/*/cloudbuild.yaml 2>/dev/null | wc -l)

echo "Variables PostgreSQL par service:"
echo "- POSTGRES_HOST=127.0.0.1: $POSTGRES_HOST_COUNT/$TOTAL_CLOUDBUILD"
echo "- POSTGRES_PORT=5432: $POSTGRES_PORT_COUNT/$TOTAL_CLOUDBUILD"
echo "- POSTGRES_DB=skillforge_db: $POSTGRES_DB_COUNT/$TOTAL_CLOUDBUILD"
echo "- POSTGRES_USER=skillforge_user: $POSTGRES_USER_COUNT/$TOTAL_CLOUDBUILD"
echo "- POSTGRES_PASSWORD=Psaumes@27: $POSTGRES_PASSWORD_COUNT/$TOTAL_CLOUDBUILD"
echo "- DATABASE_URL (correct): $DATABASE_URL_COUNT/$TOTAL_CLOUDBUILD"
echo ""

# Vérification de cohérence
ALL_CORRECT=true

if [ "$POSTGRES_HOST_COUNT" -ne "$TOTAL_CLOUDBUILD" ]; then
    echo "❌ ERREUR: POSTGRES_HOST incorrect dans certains services"
    ALL_CORRECT=false
fi

if [ "$POSTGRES_PORT_COUNT" -ne "$TOTAL_CLOUDBUILD" ]; then
    echo "❌ ERREUR: POSTGRES_PORT incorrect dans certains services"
    ALL_CORRECT=false
fi

if [ "$POSTGRES_DB_COUNT" -ne "$TOTAL_CLOUDBUILD" ]; then
    echo "❌ ERREUR: POSTGRES_DB incorrect dans certains services"
    ALL_CORRECT=false
fi

if [ "$POSTGRES_USER_COUNT" -ne "$TOTAL_CLOUDBUILD" ]; then
    echo "❌ ERREUR: POSTGRES_USER incorrect dans certains services"
    ALL_CORRECT=false
fi

if [ "$POSTGRES_PASSWORD_COUNT" -ne "$TOTAL_CLOUDBUILD" ]; then
    echo "❌ ERREUR: POSTGRES_PASSWORD incorrect dans certains services"
    ALL_CORRECT=false
fi

if [ "$DATABASE_URL_COUNT" -ne "$TOTAL_CLOUDBUILD" ]; then
    echo "❌ ERREUR: DATABASE_URL incorrect dans certains services"
    ALL_CORRECT=false
fi

echo "=== VÉRIFICATION PORTS 5433 ==="
echo ""

# Vérifier s'il reste des ports 5433
OLD_PORT_COUNT=$(grep -r "5433" apps/backend/ 2>/dev/null | grep -v ".git" | wc -l)

if [ "$OLD_PORT_COUNT" -eq 0 ]; then
    echo "✅ SUCCÈS: Aucune référence au port 5433 trouvée"
else
    echo "❌ ATTENTION: $OLD_PORT_COUNT références au port 5433 trouvées"
    echo ""
    echo "Fichiers contenant le port 5433:"
    grep -r "5433" apps/backend/ 2>/dev/null | grep -v ".git"
fi
echo ""

echo "=== LISTE DES SERVICES CONFIGURÉS ==="
echo ""

for service in $(ls apps/backend/); do
    if [ -f "apps/backend/$service/cloudbuild.yaml" ]; then
        # Vérifier si le service a toutes les variables correctes
        has_host=$(grep -c "POSTGRES_HOST=127.0.0.1" "apps/backend/$service/cloudbuild.yaml" 2>/dev/null)
        has_port=$(grep -c "POSTGRES_PORT=5432" "apps/backend/$service/cloudbuild.yaml" 2>/dev/null)
        has_db=$(grep -c "POSTGRES_DB=skillforge_db" "apps/backend/$service/cloudbuild.yaml" 2>/dev/null)
        has_user=$(grep -c "POSTGRES_USER=skillforge_user" "apps/backend/$service/cloudbuild.yaml" 2>/dev/null)
        has_password=$(grep -c "POSTGRES_PASSWORD=Psaumes@27" "apps/backend/$service/cloudbuild.yaml" 2>/dev/null)
        has_url=$(grep -c "DATABASE_URL=postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db" "apps/backend/$service/cloudbuild.yaml" 2>/dev/null)
        
        if [ "$has_host" -eq 1 ] && [ "$has_port" -eq 1 ] && [ "$has_db" -eq 1 ] && [ "$has_user" -eq 1 ] && [ "$has_password" -eq 1 ] && [ "$has_url" -eq 1 ]; then
            echo "✅ $service - Configuration complète et correcte"
        else
            echo "❌ $service - Configuration incomplète:"
            [ "$has_host" -eq 0 ] && echo "  - Manque POSTGRES_HOST=127.0.0.1"
            [ "$has_port" -eq 0 ] && echo "  - Manque POSTGRES_PORT=5432"
            [ "$has_db" -eq 0 ] && echo "  - Manque POSTGRES_DB=skillforge_db"
            [ "$has_user" -eq 0 ] && echo "  - Manque POSTGRES_USER=skillforge_user"
            [ "$has_password" -eq 0 ] && echo "  - Manque POSTGRES_PASSWORD=Psaumes@27"
            [ "$has_url" -eq 0 ] && echo "  - Manque DATABASE_URL correcte"
        fi
    else
        echo "❌ $service - Pas de cloudbuild.yaml"
    fi
done
echo ""

echo "=== RÉSUMÉ FINAL ==="
echo ""

if [ "$ALL_CORRECT" = true ] && [ "$TOTAL_SERVICES" -eq "$TOTAL_CLOUDBUILD" ] && [ "$OLD_PORT_COUNT" -eq 0 ]; then
    echo "🎉 VALIDATION RÉUSSIE!"
    echo ""
    echo "✅ Tous les services ($TOTAL_SERVICES) ont un fichier cloudbuild.yaml"
    echo "✅ Toutes les variables PostgreSQL sont correctement configurées"
    echo "✅ Tous les services utilisent le port 5432"
    echo "✅ DATABASE_URL uniforme pour tous les services"
    echo "✅ Aucune référence au port 5433"
    echo ""
    echo "Configuration PostgreSQL standardisée avec succès!"
    echo "Instance Cloud SQL: skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging"
    echo ""
    exit 0
else
    echo "❌ VALIDATION ÉCHOUÉE!"
    echo ""
    echo "Des problèmes ont été détectés dans la configuration PostgreSQL."
    echo "Veuillez corriger les erreurs mentionnées ci-dessus."
    echo ""
    exit 1
fi