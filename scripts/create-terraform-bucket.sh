#!/bin/bash
# Script pour créer le bucket GCS pour l'état Terraform
set -e

PROJECT_ID="skillforge-ai-mvp-25"
BUCKET_NAME="${PROJECT_ID}-tfstate"
REGION="europe-west1"

echo "🗂️  Création du bucket Terraform GCS"
echo "======================================"
echo "Project: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo ""

# Vérifier que gcloud est configuré
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
    echo "❌ Aucune authentification gcloud active"
    echo "Exécutez: gcloud auth login"
    exit 1
fi

# Configurer le projet
gcloud config set project "$PROJECT_ID"

# Vérifier si le bucket existe déjà
if gsutil ls -b "gs://$BUCKET_NAME" >/dev/null 2>&1; then
    echo "✅ Le bucket gs://$BUCKET_NAME existe déjà"
else
    echo "📝 Création du bucket..."
    
    # Créer le bucket avec versioning et encryption
    gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$BUCKET_NAME"
    
    # Activer le versioning pour la sécurité
    gsutil versioning set on "gs://$BUCKET_NAME"
    
    # Ajouter des labels
    gsutil label ch -l "purpose:terraform-state" "gs://$BUCKET_NAME"
    gsutil label ch -l "project:skillforge-ai" "gs://$BUCKET_NAME"
    gsutil label ch -l "environment:all" "gs://$BUCKET_NAME"
    
    echo "✅ Bucket créé avec succès: gs://$BUCKET_NAME"
fi

echo ""
echo "🔐 Configuration des permissions..."

# Ajouter des permissions pour le service account CI/CD si spécifié
if [[ -n "$GCP_CICD_SERVICE_ACCOUNT" ]]; then
    echo "Ajout des permissions pour: $GCP_CICD_SERVICE_ACCOUNT"
    gsutil iam ch "serviceAccount:$GCP_CICD_SERVICE_ACCOUNT:objectAdmin" "gs://$BUCKET_NAME"
    gsutil iam ch "serviceAccount:$GCP_CICD_SERVICE_ACCOUNT:legacyBucketReader" "gs://$BUCKET_NAME"
fi

echo ""
echo "✅ Configuration terminée !"
echo "Bucket disponible à : gs://$BUCKET_NAME"
echo ""
echo "📋 Structure des préfixes :"
echo "  - staging/    (pour l'environnement staging)"
echo "  - production/ (pour l'environnement production)"
echo ""
echo "🔄 Prochaines étapes :"
echo "1. Vérifiez que terraform/environments/*/backend.tf référence ce bucket"
echo "2. Exécutez 'terraform init' dans chaque environnement"
echo "3. Lancez le workflow Terraform"