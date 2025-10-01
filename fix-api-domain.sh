#!/bin/bash
# Script pour corriger l'erreur 404 sur api.emacsah.com
# Restaure le load balancer pour pointer vers user-service-backend-staging

set -e

echo "🔧 Fixing api.emacsah.com 404 error..."
echo "📋 Problem: Load balancer defaultService points to skillforge-shell-backend-staging instead of user-service-backend-staging"

# Import the fixed URL map configuration
echo "📥 Importing fixed URL map configuration..."
gcloud compute url-maps import skillforge-urlmap-staging \
    --source=skillforge-urlmap-fixed.yaml \
    --global \
    --quiet

echo "✅ URL map configuration updated successfully!"
echo ""
echo "🔍 Verification commands:"
echo "  curl -I https://api.emacsah.com/"
echo "  curl -I https://api.emacsah.com/health"
echo "  curl -I https://api.emacsah.com/api/v1/docs"
echo ""
echo "🕒 Changes may take 1-2 minutes to propagate..."