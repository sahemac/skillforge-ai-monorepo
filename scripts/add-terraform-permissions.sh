#!/bin/bash
# Ajouter permissions Terraform au service account sa-user-service-staging
set -e

PROJECT_ID="skillforge-ai-mvp-25"
SERVICE_ACCOUNT_EMAIL="sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com"

echo "🔐 Ajout des permissions Terraform au service account existant"
echo "==========================================================="
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Permissions Terraform requises
TERRAFORM_ROLES=(
    "roles/compute.admin"                    # Réseaux, Load Balancer, SSL, VM
    "roles/secretmanager.admin"              # Secret Manager complet
    "roles/storage.admin"                    # Storage buckets
    "roles/artifactregistry.admin"           # Artifact Registry
    "roles/cloudsql.admin"                   # Cloud SQL
    "roles/redis.admin"                      # Redis/Memorystore
    "roles/run.admin"                        # Cloud Run
    "roles/monitoring.editor"                # Monitoring dashboards/alertes
    "roles/iam.serviceAccountUser"           # Utiliser d'autres SAs
    "roles/resourcemanager.projectIamAdmin"  # Modifier IAM policies
)

echo "📝 Ajout des rôles Terraform..."
for role in "${TERRAFORM_ROLES[@]}"; do
    echo "  Adding: $role"
    if gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --condition=None >/dev/null 2>&1; then
        echo "    ✅ Added successfully"
    else
        echo "    ⚠️  Already exists or error"
    fi
done

echo ""
echo "🔍 Vérification des permissions actuelles..."
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL"

echo ""
echo "✅ Permissions Terraform ajoutées !"
echo ""
echo "🎯 Actions suivantes :"
echo "1. git push origin develop"
echo "2. Relancer workflow Terraform"
echo "3. Vérifier que tous les plans passent"