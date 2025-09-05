# 📋 SkillForge AI - Configuration Memo

## 🎯 Valeurs exactes du projet

### Google Cloud
- **Project ID**: `skillforge-ai-mvp-25`
- **Project Number**: `584748485117`
- **Region**: `europe-west1`
- **Repository**: `sahemac/skillforge-ai-monorepo`

### Workload Identity Federation
- **Pool actif**: `github-actions` (provider: `github`)
- **Full path WIF**: `projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github`
- **Audience**: `https://github.com/sahemac/skillforge-ai-monorepo`
- **Condition**: `assertion.repository=='sahemac/skillforge-ai-monorepo'`

### GitHub Secrets (4 secrets finaux)
```
GCP_PROJECT_ID = skillforge-ai-mvp-25
GCP_WIF_PROVIDER = projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github
GCP_CICD_SERVICE_ACCOUNT = [service-account]@skillforge-ai-mvp-25.iam.gserviceaccount.com
DATABASE_URL_STAGING = postgresql+asyncpg://[user]:[pass]@[ip]:5432/[db]_staging
```

### Services configurés
- **Cloud SQL**: `skillforge-postgres-staging`
- **Artifact Registry**: `skillforge-docker-repo-staging`
- **Cloud Run region**: `europe-west1`
- **Network**: `skillforge-network`

### Workflows mis à jour pour cohérence
- ✅ `deploy-user-service.yml` → Utilise GCP_WIF_PROVIDER + GCP_CICD_SERVICE_ACCOUNT
- ✅ `terraform.yml` → Mis à jour pour utiliser les mêmes secrets
- ✅ `test-secrets-config.yml` → Valide les 4 secrets requis

### Prochaines étapes Phase 3
1. Nettoyer les secrets doublons dans GitHub
2. Tester workflow `test-secrets-config.yml`
3. Lancer premier déploiement complet
4. Déboguer les problèmes restants

---
*Mémo créé Phase 2 - À conserver pour référence*