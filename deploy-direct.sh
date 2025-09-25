#!/bin/bash

# Direct deployment script for Shell Service to Cloud Run
set -e

echo "🚀 Starting direct deployment to Cloud Run"
echo "=========================================="

# Variables
PROJECT_ID="skillforge-ai-mvp-25"
REGION="us-central1"
SERVICE_NAME="skillforge-shell"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Build locally first to test
echo "📦 Building application locally..."
cd apps/frontend/shell
npm install --legacy-peer-deps || pnpm install --no-frozen-lockfile
npm run build || npx vite build

# Go back to root
cd ../../..

echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME} -f apps/frontend/shell/Dockerfile.prod apps/frontend/shell

echo "📤 Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_NAME} \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --port=80 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=10 \
  --project=${PROJECT_ID}

echo "🔗 Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)" --project=${PROJECT_ID})
echo "Service deployed at: ${SERVICE_URL}"

echo "🌐 Setting up domain mapping for skillforge-ai.emacsah.com..."
gcloud run domain-mappings create \
  --service=${SERVICE_NAME} \
  --domain=skillforge-ai.emacsah.com \
  --region=${REGION} \
  --project=${PROJECT_ID} || echo "Domain mapping may already exist"

echo "🌐 Setting up domain mapping for api.emacsah.com..."
gcloud run domain-mappings create \
  --service=${SERVICE_NAME} \
  --domain=api.emacsah.com \
  --region=${REGION} \
  --project=${PROJECT_ID} || echo "Domain mapping may already exist"

echo "✅ Deployment complete!"
echo "========================"
echo "Service URL: ${SERVICE_URL}"
echo "Custom domains:"
echo "  - https://skillforge-ai.emacsah.com"
echo "  - https://api.emacsah.com"
echo ""
echo "📝 DNS Configuration Required:"
echo "Add these records to your DNS provider:"
echo "  skillforge-ai.emacsah.com -> ghs.googlehosted.com (CNAME)"
echo "  api.emacsah.com -> ghs.googlehosted.com (CNAME)"