#!/bin/bash
# Script to configure GitHub Secrets and Google Cloud Workload Identity Federation
# Repository: sahemac/skillforge-ai-monorepo
# Project: skillforge-ai-monorepo

set -euo pipefail

# Configuration
readonly PROJECT_ID="skillforge-ai-monorepo"
readonly GITHUB_REPO="sahemac/skillforge-ai-monorepo"
readonly REGION="europe-west1"
readonly WIF_POOL_NAME="github-pool"
readonly WIF_PROVIDER_NAME="github-provider"
readonly SERVICE_ACCOUNT_NAME="github-actions"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Step 1: Get Project Number
log_info "Getting project number for $PROJECT_ID..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
log_success "Project number: $PROJECT_NUMBER"

# Step 2: Create Service Account (if not exists)
log_info "Creating service account $SERVICE_ACCOUNT_NAME..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then
    log_warn "Service account already exists"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GitHub Actions CI/CD" \
        --description="Service account for GitHub Actions CI/CD pipeline"
    log_success "Service account created"
fi

# Step 3: Grant necessary roles to the service account
log_info "Granting roles to service account..."
ROLES=(
    "roles/run.admin"                  # Cloud Run deployment
    "roles/storage.admin"               # Artifact Registry access
    "roles/iam.serviceAccountUser"     # Use service accounts
    "roles/cloudsql.client"            # Cloud SQL access
    "roles/secretmanager.secretAccessor" # Access Secret Manager
    "roles/artifactregistry.writer"    # Push Docker images
)

for role in "${ROLES[@]}"; do
    log_info "Granting $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role" \
        --quiet
done
log_success "Roles granted successfully"

# Step 4: Create Workload Identity Pool
log_info "Creating Workload Identity Pool..."
if gcloud iam workload-identity-pools describe $WIF_POOL_NAME \
    --location="global" \
    --quiet >/dev/null 2>&1; then
    log_warn "Workload Identity Pool already exists"
else
    gcloud iam workload-identity-pools create $WIF_POOL_NAME \
        --project="$PROJECT_ID" \
        --location="global" \
        --display-name="GitHub Actions Pool" \
        --description="Pool for GitHub Actions OIDC tokens"
    log_success "Workload Identity Pool created"
fi

# Step 5: Create Workload Identity Provider
log_info "Creating Workload Identity Provider..."
if gcloud iam workload-identity-pools providers describe $WIF_PROVIDER_NAME \
    --workload-identity-pool="$WIF_POOL_NAME" \
    --location="global" \
    --quiet >/dev/null 2>&1; then
    log_warn "Workload Identity Provider already exists"
else
    gcloud iam workload-identity-pools providers create-oidc $WIF_PROVIDER_NAME \
        --project="$PROJECT_ID" \
        --location="global" \
        --workload-identity-pool="$WIF_POOL_NAME" \
        --display-name="GitHub Actions Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
        --issuer-uri="https://token.actions.githubusercontent.com" \
        --attribute-condition="assertion.repository == '$GITHUB_REPO'"
    log_success "Workload Identity Provider created"
fi

# Step 6: Allow the GitHub repository to use the service account
log_info "Configuring repository access to service account..."
gcloud iam service-accounts add-iam-policy-binding \
    "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --project="$PROJECT_ID" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$WIF_POOL_NAME/attribute.repository/$GITHUB_REPO"
log_success "Repository access configured"

# Step 7: Create Cloud SQL instances (if not exists)
log_info "Checking Cloud SQL instances..."
if gcloud sql instances describe skillforge-postgres-staging --project=$PROJECT_ID >/dev/null 2>&1; then
    log_warn "Cloud SQL staging instance already exists"
else
    log_info "Creating Cloud SQL staging instance..."
    gcloud sql instances create skillforge-postgres-staging \
        --database-version=POSTGRES_15 \
        --tier=db-g1-small \
        --region=$REGION \
        --network=projects/$PROJECT_ID/global/networks/skillforge-network \
        --no-assign-ip \
        --database-flags=max_connections=100 \
        --backup-start-time=03:00 \
        --backup-location=$REGION \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=03 \
        --maintenance-release-channel=production
    
    # Create database
    gcloud sql databases create skillforge_staging \
        --instance=skillforge-postgres-staging
    
    # Create user
    gcloud sql users create skillforge_user \
        --instance=skillforge-postgres-staging \
        --password=CHANGE_THIS_PASSWORD_STAGING
    
    log_success "Cloud SQL staging instance created"
fi

# Step 8: Create Artifact Registry repository
log_info "Creating Artifact Registry repository..."
if gcloud artifacts repositories describe skillforge-docker-repo-staging \
    --location=$REGION \
    --quiet >/dev/null 2>&1; then
    log_warn "Artifact Registry repository already exists"
else
    gcloud artifacts repositories create skillforge-docker-repo-staging \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker images for SkillForge AI staging"
    log_success "Artifact Registry repository created"
fi

# Step 9: Output values for GitHub Secrets
log_info "===========================================" 
log_success "Setup completed successfully!"
log_info "==========================================="
echo ""
log_info "Add these secrets to GitHub Repository Settings → Secrets and variables → Actions:"
echo ""
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GCP_WIF_PROVIDER=projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$WIF_POOL_NAME/providers/$WIF_PROVIDER_NAME"
echo "GCP_CICD_SERVICE_ACCOUNT=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo ""
log_warn "⚠️  IMPORTANT: You need to manually set the DATABASE_URL_STAGING secret with the actual password!"
echo "DATABASE_URL_STAGING=postgresql+asyncpg://skillforge_user:YOUR_PASSWORD@CLOUD_SQL_IP:5432/skillforge_staging"
echo ""
log_info "To get the Cloud SQL private IP:"
echo "gcloud sql instances describe skillforge-postgres-staging --format='value(ipAddresses[0].ipAddress)'"
echo ""
log_success "Script completed! Please add the secrets to GitHub manually."