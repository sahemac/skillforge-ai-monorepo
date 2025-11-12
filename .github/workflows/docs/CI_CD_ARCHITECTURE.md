# Architecture CI/CD - SkillForge AI

## Vue d'ensemble

SkillForge AI utilise une architecture CI/CD moderne et automatisée basée sur GitHub Actions et Google Cloud Platform (GCP). Cette architecture garantit des déploiements sûrs, testés et progressifs vers la production.

## Schéma global

```
┌─────────────────────────────────────────────────────────────────┐
│                        Pull Request                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Branch Protection (branch-protection.yml)               │  │
│  │  • Conventional commits validation                        │  │
│  │  • Backend tests (PostgreSQL + Redis)                    │  │
│  │  • Frontend tests (Vitest)                               │  │
│  │  • Security scanning (Trivy)                             │  │
│  │  • Automated PR summary                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                   │
│                      [Merge Approved]                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STAGING ENVIRONMENT                          │
│                     (develop branch)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Auto-Deploy Staging (deploy-staging-auto.yml)           │  │
│  │  • Change detection (backend/frontend/packages)          │  │
│  │  • Deploy to Cloud Run Staging                           │  │
│  │  • Backend smoke tests                                    │  │
│  │  • Frontend smoke tests                                   │  │
│  │  • E2E tests (Playwright)                                │  │
│  │  • Deployment summary & notifications                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Environment URLs:                                              │
│  • Frontend: https://skillforge-ai.emacsah.com                 │
│  • User API: https://skillforge-user-service-staging-...       │
│  • Company API: https://skillforge-company-service-staging-... │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Tests Passed in Staging]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCTION ENVIRONMENT                         │
│                      (main branch)                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Standard Production Deploy (deploy-production.yml)       │  │
│  │  ⏸  Manual approval required                              │  │
│  │  • Pre-deployment validation                              │  │
│  │  • Database backup                                        │  │
│  │  • Deploy to Cloud Run Production                        │  │
│  │  • Production smoke tests                                 │  │
│  │  • Post-deployment monitoring                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       OR                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Canary Deployment (canary-deployment.yml)               │  │
│  │  ⏸  Manual trigger only                                   │  │
│  │  • Deploy with 0% traffic                                 │  │
│  │  • Canary 10% → Monitor 5 min                            │  │
│  │  • Canary 50% → Monitor 5 min                            │  │
│  │  • Canary 100% → Complete                                │  │
│  │  • Auto-rollback on errors                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Environment URLs:                                              │
│  • Frontend: https://skillforge-ai.emacsah.com (production)    │
│  • User API: https://skillforge-user-service-production-...    │
│  • Company API: https://skillforge-company-service-prod-...    │
└─────────────────────────────────────────────────────────────────┘
```

## Workflows détaillés

### 1. Branch Protection (`branch-protection.yml`)

**Déclencheur**: Pull Request vers `develop` ou `main`

**Objectif**: Garantir la qualité du code avant merge

**Jobs**:
- `validate-pr`: Validation PR (titre, description, taille)
- `backend-tests`: Tests backend avec services Docker
- `frontend-tests`: Tests frontend avec pnpm et Vitest
- `security-scan`: Scan de sécurité avec Trivy
- `pr-validation-summary`: Résumé et commentaire automatique

**Services Docker**:
- PostgreSQL 15-alpine (port 5432)
- Redis 7-alpine (port 6379)

**Durée moyenne**: 8-12 minutes

**Documentation**: [BRANCH_PROTECTION.md](./BRANCH_PROTECTION.md)

---

### 2. Auto-Deploy Staging (`deploy-staging-auto.yml`)

**Déclencheur**: Push vers `develop`

**Objectif**: Déploiement automatique vers l'environnement de staging

**Jobs**:
1. `detect-changes`: Détection des changements
2. `deploy-backend`: Déploiement services backend (si changés)
3. `deploy-frontend`: Déploiement apps frontend (si changées)
4. `smoke-tests-backend`: Tests rapides backend
5. `smoke-tests-frontend`: Tests rapides frontend
6. `e2e-tests`: Tests end-to-end avec Playwright
7. `deployment-summary`: Résumé et notifications

**Concurrency**: `deploy-staging` (pas de déploiements parallèles)

**Durée moyenne**: 15-25 minutes

**Documentation**: [STAGING_DEPLOYMENT.md](./STAGING_DEPLOYMENT.md)

---

### 3. Production Deployment (`deploy-production.yml`)

**Déclencheur**: Push vers `main`

**Objectif**: Déploiement sécurisé vers production avec approbation manuelle

**Jobs**:
1. `pre-deployment-checks`: Validation pré-déploiement
2. `approval-gate`: ⏸ Approbation manuelle requise
3. `pre-deployment-backup`: Backup base de données
4. `deploy-backend`: Déploiement backend
5. `deploy-frontend`: Déploiement frontend
6. `smoke-tests-backend`: Tests production backend
7. `smoke-tests-frontend`: Tests production frontend
8. `post-deployment-validation`: Validation finale

**Protection GitHub Environment**: `production`

**Durée moyenne**: 20-30 minutes (+ temps d'approbation)

**Documentation**: [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)

---

### 4. Canary Deployment (`canary-deployment.yml`)

**Déclencheur**: Manuel uniquement (`workflow_dispatch`)

**Objectif**: Déploiement progressif en production avec rollback automatique

**Phases**:
1. `prepare-canary`: Préparation et configuration
2. `deploy-new-revision`: Déploiement avec 0% trafic
3. `canary-10-percent`: 10% trafic → Monitoring 5 min
4. `canary-50-percent`: 50% trafic → Monitoring 5 min
5. `canary-100-percent`: 100% trafic → Complet
6. `deployment-summary`: Résumé final

**Auto-rollback**: Sur détection d'erreurs (> 10 erreurs/minute)

**Durée totale**: ~20-25 minutes

**Documentation**: [CANARY_DEPLOYMENT.md](./CANARY_DEPLOYMENT.md)

---

### 5. E2E Tests (`e2e-tests-staging.yml`)

**Déclencheur**: Appelé par `deploy-staging-auto.yml` ou manuel

**Objectif**: Tests end-to-end complets sur l'environnement de staging

**Suites de tests**:
- `e2e-frontend`: Tests Playwright multi-browsers
- `e2e-api`: Tests endpoints API
- `performance-tests`: Tests de performance
- `test-summary`: Résumé des résultats

**Browsers testés**: Chromium, Firefox, WebKit

**Sharding**: Tests parallélisés (2 shards par browser)

**Durée moyenne**: 10-15 minutes

**Documentation**: [E2E_TESTS.md](./E2E_TESTS.md)

---

### 6. Smoke Tests (`smoke-tests.yml`)

**Déclencheur**: Appelé après déploiements

**Objectif**: Validation rapide post-déploiement

**Tests**:
- Health check avec retry (max 5 tentatives)
- Homepage load test
- Static assets validation
- Performance check (< 5s response time)
- Security headers validation
- Navigation routes testing

**Durée moyenne**: 2-3 minutes

**Documentation**: [SMOKE_TESTS.md](./SMOKE_TESTS.md)

## Environnements

### Staging
- **Branch**: `develop`
- **Déploiement**: Automatique sur push
- **Cloud Run**: `*-staging` services
- **Base de données**: `skillforge-pg-instance-staging`
- **Domaine**: https://skillforge-ai.emacsah.com

### Production
- **Branch**: `main`
- **Déploiement**: Avec approbation manuelle
- **Cloud Run**: `*-production` services
- **Base de données**: `skillforge-pg-instance-production`
- **Domaine**: https://skillforge-ai.emacsah.com (production)

## Stratégies de déploiement

### Déploiement Standard
Pour la majorité des changements non-critiques:
1. Merge PR vers `develop`
2. Tests automatiques en staging
3. Validation manuelle en staging
4. Merge vers `main`
5. Approbation manuelle
6. Déploiement production

### Déploiement Canary
Pour les changements critiques ou à haut risque:
1. Code validé en staging
2. Merge vers `main`
3. Déclencher manuellement le workflow canary
4. Surveillance progressive (10% → 50% → 100%)
5. Rollback automatique si erreurs détectées

### Hotfix
Pour les corrections urgentes:
1. Créer branche depuis `main`
2. Fix + tests
3. Merge direct vers `main` (après approbation accélérée)
4. Déploiement production immédiat
5. Backport vers `develop`

## Sécurité

### Secrets Management
- Tous les secrets stockés dans **GitHub Secrets**
- Secrets GCP dans **Google Secret Manager**
- Accès restreint par service account

### Workload Identity Federation
- Authentification sans clés avec GCP
- Rotation automatique des credentials
- Principe du moindre privilège

### Scans de sécurité
- **Trivy**: Scan de vulnérabilités
- **Bandit**: Analyse sécurité Python
- **Safety**: Vérification dépendances Python
- **Semgrep**: Analyse statique de code

## Monitoring & Observabilité

### Logs
- **GitHub Actions**: Logs de workflows
- **Cloud Logging**: Logs services GCP
- **Structured Logging**: Format JSON standardisé

### Métriques
- **Cloud Monitoring**: Métriques infrastructure
- **Custom Metrics**: Métriques métier
- **Workflow Duration**: Temps d'exécution CI/CD

### Alertes
- **Slack**: Notifications déploiements
- **Email**: Alertes GitHub
- **Cloud Monitoring**: Alertes infrastructure

## Rollback

### Automatique
- Workflow canary: rollback si > 10 erreurs/min
- Health checks: échec après 15 tentatives

### Manuel

**Via GitHub Actions**:
```bash
gh workflow run canary-deployment.yml -f service=shell
```

**Via gcloud CLI**:
```bash
# Lister les révisions
gcloud run revisions list --service=skillforge-frontend-shell-production --region=europe-west1

# Rollback
gcloud run services update-traffic skillforge-frontend-shell-production \
  --region=europe-west1 \
  --to-revisions=<previous-revision>=100
```

**Via script helper**:
```bash
./scripts/canary-rollback.sh skillforge-frontend-shell-production
```

## Bonnes pratiques

### Pour les développeurs

1. **Toujours** créer une PR vers `develop` (jamais direct vers `main`)
2. **Respecter** le format Conventional Commits pour les PR
3. **Ajouter** une description détaillée à chaque PR
4. **Vérifier** que les tests passent en local avant de push
5. **Surveiller** les déploiements staging après merge

### Pour les mainteneurs

1. **Approuver** les PR seulement si tous les checks passent
2. **Tester** manuellement en staging avant merge vers main
3. **Planifier** les déploiements production (éviter vendredi soir!)
4. **Surveiller** les métriques pendant 15 min après déploiement production
5. **Documenter** tout incident dans un post-mortem

## Dépannage

### Workflow bloqué

```bash
# Vérifier le statut
gh run list --workflow=deploy-staging-auto.yml --limit 5

# Voir les logs
gh run view <run-id> --log

# Annuler une exécution
gh run cancel <run-id>
```

### Tests échouent en CI mais pas en local

- Vérifier les variables d'environnement
- Vérifier les versions de dépendances
- Consulter les logs détaillés du job

### Déploiement production échoue

1. Vérifier les logs Cloud Run
2. Vérifier les secrets GCP
3. Vérifier les permissions IAM
4. Considérer un rollback

## Ressources

- [Guide de démarrage rapide](./QUICK_START.md)
- [Documentation workflows](./README.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

## Contact & Support

- **DevOps Team**: DevOps channel sur Slack
- **Incidents**: Créer une issue GitHub avec le label `incident`
- **Questions**: Discussions GitHub ou Slack #devops
