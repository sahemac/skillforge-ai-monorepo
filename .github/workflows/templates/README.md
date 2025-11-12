# Workflow Templates - SkillForge AI

## 📋 Overview

This directory contains **reusable GitHub Actions workflow templates** for deploying new services. Use these templates when implementing new services to ensure consistent CI/CD practices across the monorepo.

## 🎯 Philosophy: Just-In-Time Workflow Creation

**We do NOT create workflows for services that don't exist yet.**

### Why?
- ❌ Pre-created workflows become obsolete before the service is implemented
- ❌ Maintenance overhead: updating 25 workflows vs 12 active workflows
- ❌ Architecture changes make early workflows wrong
- ✅ Templates adapt to real needs discovered during implementation
- ✅ Clear signal: if workflow exists = service is deployed
- ✅ 5-10 minutes to create from template vs hours maintaining dormant workflows

---

## 📊 Service Status Inventory

### ✅ Deployed Services (Workflows Exist)
| Service | Workflow | Status | URL |
|---------|----------|--------|-----|
| **user-service** | `deploy-user-service.yml` | 🟢 Active | staging-user-service.run.app |
| **auth-service** | `deploy-auth-service.yml` | 🟢 Active | staging-auth-service.run.app |
| **company-service** | `deploy-company-service.yml` | 🟢 Active | staging-company-service.run.app |
| **shell (frontend)** | `deploy-shell-service.yml` | 🟢 Active | skillforge-ai-shell-staging.run.app |

### 🚧 In Development (Workflows Will Be Created)
| Service | Priority | Expected Template | Notes |
|---------|----------|-------------------|-------|
| **project-service** | High | backend-fastapi | Basic structure exists |
| **notification-service** | Medium | backend-fastapi | Email/push notifications |
| **api-gateway** | Medium | backend-fastapi | Unified API entry point |

### 📅 Planned Services (Create Workflow When Ready)
| Service | Type | Template | Implementation Notes |
|---------|------|----------|----------------------|
| analytics-service | ML/Data | ml-service | Databricks integration |
| matching-service | ML | ml-service | AI-powered learner-project matching |
| recommendation-service | ML | ml-service | Personalized recommendations |
| chat-messaging-service | Backend | backend-fastapi | Real-time messaging |
| portfolio-service | Backend | backend-fastapi | Learner portfolios |
| evaluation-service | Backend | backend-fastapi | Project evaluations |
| gamification-service | Backend | backend-fastapi | Badges, points, leaderboards |
| scheduling-service | Backend | backend-fastapi | Calendar, availability |
| search-service | Backend | backend-fastapi | Elasticsearch integration |
| storage-service | Backend | backend-fastapi | File uploads, S3 |
| subscription-service | Backend | backend-fastapi | Payments, Stripe |
| workflow-service | Backend | backend-fastapi | Approval workflows |
| integration-service | Backend | backend-fastapi | Third-party APIs |
| realtime-collaboration-service | Backend | backend-fastapi | WebSocket, collaborative editing |

---

## 🚀 How to Create a New Workflow

### Step 1: Choose the Right Template

| Template | Use When | Examples |
|----------|----------|----------|
| `template-backend-fastapi.yml` | Python FastAPI service with PostgreSQL | user-service, auth-service, notification-service |
| `template-frontend-react.yml` | React SPA with module federation | shell, admin, company, learner apps |
| `template-ml-service.yml` | ML/AI service with model serving | analytics, matching, recommendation |

### Step 2: Copy and Customize

```bash
# Example: Creating workflow for notification-service

# 1. Copy the appropriate template
cp .github/workflows/templates/template-backend-fastapi.yml \
   .github/workflows/deploy-notification-service.yml

# 2. Open the file and replace ALL placeholders:
# Find: {{SERVICE_NAME}}        Replace with: notification-service
# Find: {{SERVICE_PATH}}        Replace with: apps/backend/notification-service
# Find: {{SERVICE_PORT}}        Replace with: 8003
# Find: {{SERVICE_DESCRIPTION}} Replace with: Send email and push notifications

# 3. Review and adjust:
#    - Database migration needs? (has_migration: true/false)
#    - Special dependencies? (Redis, external APIs, etc.)
#    - Environment variables?
#    - Service account permissions?

# 4. Test locally first (if possible)
```

### Step 3: Create Service Account (GCP)

```bash
# Create service account for new service
SERVICE=notification-service
ENVIRONMENT=staging

gcloud iam service-accounts create sa-${SERVICE}-${ENVIRONMENT} \
  --display-name="Service account for ${SERVICE} (${ENVIRONMENT})" \
  --project=skillforge-ai-mvp-25

# Grant necessary permissions
for role in roles/cloudsql.client roles/logging.logWriter roles/monitoring.metricWriter; do
  gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:sa-${SERVICE}-${ENVIRONMENT}@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="$role"
done

# Grant secret access (adjust secrets as needed)
for secret in DATABASE_URL SECRET_KEY SMTP_PASSWORD; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:sa-${SERVICE}-${ENVIRONMENT}@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Step 4: Validation Checklist

Before committing your new workflow, verify:

- [ ] All `{{PLACEHOLDERS}}` replaced with actual values
- [ ] Service name matches directory structure exactly
- [ ] Service account created in GCP with proper permissions
- [ ] Secrets configured (DATABASE_URL, API keys, etc.)
- [ ] `paths:` filter includes correct service directory
- [ ] Workflow triggers are appropriate (push, PR, workflow_dispatch)
- [ ] Environment-specific configuration (staging/production)
- [ ] Health check endpoint configured
- [ ] Rollback strategy defined (for production)
- [ ] Dockerfile exists and builds successfully
- [ ] requirements.txt or package.json exists
- [ ] Database migrations prepared (if applicable)

### Step 5: Test and Commit

```bash
# Add workflow
git add .github/workflows/deploy-notification-service.yml

# Commit with clear message
git commit -m "feat(ci): Add deployment workflow for notification-service

- Based on backend-fastapi template
- Configured for staging environment
- Service account: sa-notification-service-staging
- Triggers on push to apps/backend/notification-service/**"

# Push and monitor
git push origin feature/your-branch

# Watch the workflow run
gh run watch
```

---

## 📚 Template Reference

### Backend FastAPI Template

**File:** `template-backend-fastapi.yml`

**Features:**
- Python 3.11 + FastAPI
- PostgreSQL + Alembic migrations
- Cloud Run deployment
- Trivy security scanning
- Pytest test suite
- Health check validation
- Automatic rollback (production)

**Required Secrets:**
- `GCP_WIF_PROVIDER`
- `GCP_CICD_SERVICE_ACCOUNT`
- `DATABASE_URL`
- `SECRET_KEY`

**Configuration Points:**
- Service name
- Service path
- Port number
- Database migration (yes/no)
- Python version
- Dependencies

---

### Frontend React Template

**File:** `template-frontend-react.yml`

**Features:**
- React 18 + TypeScript
- Vite build system
- pnpm package manager
- Module federation support
- Nginx serving
- Cloud Run deployment
- E2E testing with Playwright (optional)

**Required Secrets:**
- `GCP_WIF_PROVIDER`
- `GCP_CICD_SERVICE_ACCOUNT`
- `VITE_API_BASE_URL` (runtime config)

**Configuration Points:**
- App name
- Build output directory
- Environment variables
- Module federation config

---

### ML Service Template

**File:** `template-ml-service.yml`

**Features:**
- Python ML frameworks (scikit-learn, TensorFlow, PyTorch)
- Model serving with FastAPI
- GPU support (optional)
- Model versioning
- A/B testing ready
- Feature store integration
- Cloud Run with larger memory/CPU

**Required Secrets:**
- `GCP_WIF_PROVIDER`
- `GCP_CICD_SERVICE_ACCOUNT`
- `ML_MODEL_BUCKET` (GCS bucket for models)
- `MLFLOW_TRACKING_URI` (optional)

**Configuration Points:**
- Model framework
- GPU requirements
- Memory/CPU allocation
- Prediction endpoints
- Batch vs real-time

---

## 🔧 Common Customizations

### Adding Redis Dependency

```yaml
# In your service workflow, add to setup steps:
- name: Setup Redis connection
  run: |
    echo "REDIS_URL=${{ secrets.REDIS_URL }}" >> .env
```

### Adding External API Keys

```yaml
# Create secret in GitHub repo settings:
# Settings > Secrets > Actions > New repository secret

# In workflow:
env:
  SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
  STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
```

### Custom Build Steps

```yaml
# Example: Compiling Protocol Buffers
- name: Generate protobuf code
  run: |
    python -m grpc_tools.protoc \
      --python_out=. \
      --grpc_python_out=. \
      protos/*.proto
```

### Multi-Region Deployment

```yaml
strategy:
  matrix:
    region: [europe-west1, us-central1, asia-east1]
steps:
  - name: Deploy to ${{ matrix.region }}
    run: |
      gcloud run deploy $SERVICE_NAME \
        --region=${{ matrix.region }} \
        # ... other flags
```

---

## 🎓 Best Practices

### 1. Service Naming Convention

```
Format: {domain}-service
Examples:
  ✅ user-service
  ✅ notification-service
  ✅ chat-messaging-service
  ❌ users (too generic)
  ❌ notificationService (camelCase not used)
```

### 2. Workflow Naming Convention

```
Format: deploy-{service-name}.yml
Examples:
  ✅ deploy-user-service.yml
  ✅ deploy-notification-service.yml
  ❌ notification.yml (unclear purpose)
  ❌ deploy_notification_service.yml (underscores not used)
```

### 3. Trigger Configuration

```yaml
# DO: Specific paths to avoid unnecessary runs
on:
  push:
    branches: [main, develop]
    paths:
      - 'apps/backend/notification-service/**'
      - '.github/workflows/deploy-notification-service.yml'

# DON'T: Trigger on all changes
on:
  push:
    branches: [main, develop]
```

### 4. Environment Separation

```yaml
# Staging: Auto-deploy on push to develop
on:
  push:
    branches: [develop]

# Production: Manual approval required
on:
  workflow_dispatch:
    inputs:
      confirm_production:
        description: 'Type "DEPLOY" to confirm production deployment'
        required: true
```

### 5. Secrets Management

```bash
# DO: Use Secret Manager for runtime secrets
gcloud secrets create SENDGRID_API_KEY --data-file=sendgrid.key

# DON'T: Hardcode secrets in workflows
env:
  API_KEY: "sk-1234567890"  # ❌ NEVER DO THIS
```

---

## 🆘 Troubleshooting

### Workflow not triggering?

```bash
# Check path filters match your changes
git diff --name-only origin/main...HEAD

# Verify workflow syntax
actionlint .github/workflows/deploy-your-service.yml
```

### Service account permissions error?

```bash
# Verify service account exists
gcloud iam service-accounts list --filter="email:sa-your-service"

# Check IAM bindings
gcloud projects get-iam-policy skillforge-ai-mvp-25 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:sa-your-service-staging*"
```

### Cloud Run deployment fails?

```bash
# Check service logs
gcloud run services describe your-service --region=europe-west1

# View deployment logs
gh run view --log-failed
```

---

## 📝 Template Maintenance

### When to Update Templates

Update templates when:
- ✅ Common pattern emerges across multiple services
- ✅ Security best practice changes
- ✅ GCP/GitHub Actions updates available
- ✅ New compliance requirement added

### How to Update

1. Update the template file
2. Add changelog entry in this README
3. Notify team in Slack/email
4. Consider updating existing workflows (gradual migration)

---

## 📞 Support

**Questions?**
- Check existing workflows: `.github/workflows/deploy-*-service.yml`
- Review deploy-service.yml (reusable workflow)
- Ask in #devops Slack channel

**Found a bug in template?**
- Create issue: "Template bug: [description]"
- PR welcome with fix

---

**Last Updated:** 2025-11-07
**Maintained by:** DevOps Team
**Version:** 1.0.0
