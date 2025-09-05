#!/bin/bash
# Script de diagnostic Workload Identity Federation
set -e

echo "🔍 Diagnostic Workload Identity Federation"
echo "=========================================="

PROJECT_ID="skillforge-ai-mvp-25"
PROJECT_NUMBER="584748485117"
POOL_NAME="github-actions"
PROVIDER_NAME="github"
REPO="sahemac/skillforge-ai-monorepo"

echo ""
echo "📋 Configuration attendue :"
echo "Project ID: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "Repository: $REPO"
echo ""

# Vérifier que gcloud est configuré
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
    echo "❌ Aucune authentification gcloud active"
    echo "Exécutez: gcloud auth login"
    exit 1
fi

echo "✅ Authentification gcloud active"
echo ""

# Vérifier le projet actuel
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [[ "$CURRENT_PROJECT" != "$PROJECT_ID" ]]; then
    echo "⚠️  Projet gcloud actuel: $CURRENT_PROJECT"
    echo "📝 Configuration du projet correct..."
    gcloud config set project "$PROJECT_ID"
fi

echo "✅ Projet configuré: $PROJECT_ID"
echo ""

# Vérifier l'existence du pool WIF
echo "🔍 Vérification du pool Workload Identity..."
if gcloud iam workload-identity-pools describe "$POOL_NAME" \
    --location="global" \
    --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ Pool WIF existe: $POOL_NAME"
else
    echo "❌ Pool WIF introuvable: $POOL_NAME"
    echo "📝 Création du pool..."
    gcloud iam workload-identity-pools create "$POOL_NAME" \
        --project="$PROJECT_ID" \
        --location="global" \
        --display-name="GitHub Actions Pool"
fi

# Vérifier l'existence du provider
echo ""
echo "🔍 Vérification du provider GitHub..."
if gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --workload-identity-pool="$POOL_NAME" \
    --location="global" \
    --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ Provider GitHub existe: $PROVIDER_NAME"
else
    echo "❌ Provider GitHub introuvable: $PROVIDER_NAME"
    echo "📝 Création du provider..."
    gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
        --project="$PROJECT_ID" \
        --location="global" \
        --workload-identity-pool="$POOL_NAME" \
        --display-name="GitHub Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --issuer-uri="https://token.actions.githubusercontent.com"
fi

# Afficher la configuration actuelle du provider
echo ""
echo "🔍 Configuration actuelle du provider:"
gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --workload-identity-pool="$POOL_NAME" \
    --location="global" \
    --project="$PROJECT_ID" \
    --format="yaml(displayName,state,attributeMapping,attributeCondition,oidc)"

echo ""
echo "📝 URLs de configuration:"
echo "WIF Provider: projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"
echo "Audience: https://github.com/$REPO"
echo ""

# Lister les service accounts disponibles
echo "🔍 Service accounts disponibles:"
gcloud iam service-accounts list \
    --project="$PROJECT_ID" \
    --format="table(email,displayName)"

echo ""
echo "📝 Prochaines étapes:"
echo "1. Vérifiez que votre service account existe dans la liste ci-dessus"
echo "2. Configurez le mapping IAM pour autoriser le repository"
echo "3. Testez l'authentification depuis GitHub Actions"