#!/bin/bash

# Canary Rollback Script
# Usage: ./scripts/canary-rollback.sh <service-name> <revision-name>

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GCP_PROJECT_ID="skillforge-ai-mvp-25"
GCP_REGION="europe-west1"

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    cat << EOF
Usage: $0 <service-name> [<revision-name>]

Rollback a canary deployment to a previous revision.

Arguments:
  service-name    Service name (e.g., skillforge-frontend-shell-production)
  revision-name   Target revision (optional, defaults to previous stable)

Examples:
  $0 skillforge-frontend-shell-production
  $0 skillforge-user-service-production skillforge-user-service-production-00042-abc

EOF
    exit 1
}

# Main
if [ $# -lt 1 ]; then
    print_error "Missing required arguments"
    show_usage
fi

SERVICE_NAME="$1"
TARGET_REVISION="${2:-}"

print_info "Starting rollback for service: $SERVICE_NAME"

# Get current traffic split
print_info "Fetching current traffic split..."
CURRENT_TRAFFIC=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$GCP_REGION" \
    --format="table(status.traffic[].revisionName,status.traffic[].percent)")

echo "$CURRENT_TRAFFIC"

# If no target revision specified, find the previous stable one
if [ -z "$TARGET_REVISION" ]; then
    print_info "No target revision specified, finding previous stable revision..."

    TARGET_REVISION=$(gcloud run revisions list \
        --service="$SERVICE_NAME" \
        --region="$GCP_REGION" \
        --format="value(metadata.name)" \
        --sort-by="~metadata.creationTimestamp" \
        --limit=2 | tail -1)

    print_info "Target revision: $TARGET_REVISION"
fi

# Confirm rollback
read -p "Do you want to rollback to $TARGET_REVISION? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    print_warn "Rollback cancelled"
    exit 0
fi

# Perform rollback
print_info "Rolling back to $TARGET_REVISION..."

gcloud run services update-traffic "$SERVICE_NAME" \
    --region="$GCP_REGION" \
    --to-revisions="$TARGET_REVISION=100"

print_info "✅ Rollback complete!"

# Verify rollback
print_info "Verifying rollback..."

NEW_TRAFFIC=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$GCP_REGION" \
    --format="table(status.traffic[].revisionName,status.traffic[].percent)")

echo "$NEW_TRAFFIC"

# Health check
print_info "Running health check..."

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$GCP_REGION" \
    --format='value(status.url)')

HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/health" || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    print_info "✅ Health check passed (HTTP $HEALTH_RESPONSE)"
else
    print_warn "⚠️ Health check returned HTTP $HEALTH_RESPONSE"
fi

print_info "Rollback complete! Monitor the service for any issues."
