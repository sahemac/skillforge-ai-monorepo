#!/bin/bash

# Script de déploiement pour SkillForge AI Shell Service
# Utilise GitHub Actions pour automatiser le déploiement

set -e

echo "🚀 Début du déploiement du Shell Service"
echo "================================="

# Vérification des prérequis
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI n'est pas installé - utilisation de git normal"
fi

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="shell"
ENVIRONMENT="${1:-staging}"

echo "📁 Répertoire de projet: $PROJECT_DIR"
echo "🏷️  Service: $SERVICE_NAME"
echo "🌍 Environnement: $ENVIRONMENT"

# Vérification de l'état du repository
cd "$PROJECT_DIR"

echo ""
echo "📊 État du repository Git"
echo "========================"
git status --porcelain

# Staging des changements importants
echo ""
echo "📦 Préparation des fichiers pour le déploiement"
echo "=============================================="

# Ajouter les fichiers de configuration de déploiement
git add apps/frontend/shell/cloudbuild-deploy.yaml 2>/dev/null || echo "cloudbuild-deploy.yaml déjà stagé"
git add apps/frontend/shell/Dockerfile* 2>/dev/null || echo "Dockerfiles déjà stagés"
git add apps/backend/notification-service/ 2>/dev/null || echo "notification-service déjà stagé"

# Commit des changements
echo ""
echo "💾 Commit des changements"
echo "========================"

if [ -z "$(git diff --staged)" ]; then
    echo "ℹ️  Aucun changement à commiter"
else
    git commit -m "feat: Deploy Shell service with notification-service backend

- Add Cloud Build configuration for Shell deployment
- Complete notification-service implementation
- Ready for staging deployment

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

    echo "✅ Commit créé avec succès"
fi

# Push vers le repository
echo ""
echo "⬆️  Push vers GitHub"
echo "==================="

git push origin develop

echo "✅ Push réussi vers la branche develop"

# Déclencher le workflow GitHub Actions
echo ""
echo "🎯 Déclenchement du déploiement automatique"
echo "=========================================="

if command -v gh &> /dev/null; then
    echo "🚀 Déclenchement via GitHub CLI..."
    gh workflow run "deploy-shell-service.yml" \
        --field environment="$ENVIRONMENT" \
        --field force_deploy=true

    echo "✅ Workflow déclenché avec succès"
    echo ""
    echo "🔍 Pour suivre le déploiement:"
    echo "   gh run list --workflow=deploy-shell-service.yml"
    echo "   ou visitez: https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/actions"
else
    echo "ℹ️  GitHub CLI non disponible - le déploiement se déclenchera automatiquement"
    echo "   grâce au trigger sur push vers develop"
fi

echo ""
echo "🎉 Déploiement initié avec succès!"
echo "================================="
echo ""
echo "📋 Étapes suivantes:"
echo "   1. Le workflow GitHub Actions va démarrer automatiquement"
echo "   2. L'image Docker sera construite et poussée vers Artifact Registry"
echo "   3. Le service sera déployé sur Cloud Run"
echo "   4. L'URL de déploiement sera affichée dans les logs du workflow"
echo ""
echo "🔗 Liens utiles:"
echo "   - Actions: https://github.com/YOUR_ORG/skillforge-ai-monorepo/actions"
echo "   - Cloud Console: https://console.cloud.google.com/run?project=skillforge-ai-mvp-25"
echo ""
echo "⏱️  Temps estimé de déploiement: 5-10 minutes"