# Frontend Deployment Workflow

## Vue d'ensemble

Ce workflow gère le déploiement automatisé de toutes les applications frontend de SkillForge AI sur Google Cloud Run.

**Fichier**: `frontend-deploy.yml`

## Déclencheurs

### Push automatique
- Branches: `main`, `develop`
- Chemins surveillés:
  - `apps/frontend/**`
  - `packages/shared/**`
  - `packages/core/**`
  - `.github/workflows/frontend-deploy.yml`

### Pull Request
- Branches cibles: `main`, `develop`
- Chemins surveillés: Identiques au push

### Déclenchement manuel (`workflow_dispatch`)
Paramètres disponibles:
- **environment**: staging ou production (défaut: staging)
- **apps**: Liste d'apps séparées par virgule ou "all" (défaut: all)
- **force_rebuild**: Force le rebuild complet (défaut: false)

## Architecture du Workflow

### Jobs principaux

#### 1. `detect-changes`
- Détecte les fichiers modifiés
- Génère la matrice de build
- Calcule les clés de cache
- Détermine l'environnement de déploiement

**Outputs**:
- `shell`, `auth`, `admin`, `company`, `learner`: Applications modifiées (true/false)
- `shared_changed`: Packages partagés modifiés (true/false)
- `matrix`: Matrice d'applications à déployer
- `environment`: staging ou production
- `cache_key`: Clé de cache pour les dépendances
- `build_hash`: Hash pour le cache de build

#### 2. `test`
- Installe les dépendances via pnpm
- Configure le cache des modules
- Exécute les tests unitaires avec Vitest
- Génère les rapports de couverture

**Dépendances**: detect-changes

#### 3. `build`
- Build parallèle de toutes les applications modifiées
- Utilise la matrice de déploiement
- Cache des dépendances et builds
- Optimisations Vite activées

**Dépendances**: test

#### 4. `docker`
- Construit les images Docker
- Tag avec le hash du commit
- Push vers Artifact Registry GCP

**Dépendances**: build

#### 5. `deploy`
- Déploie sur Cloud Run
- Configure l'ingress et IAM
- Update du Load Balancer

**Dépendances**: docker

#### 6. `notify`
- Notifications Slack en cas d'erreur
- Summary des déploiements

**Dépendances**: deploy (always runs)

## Variables d'environnement

### Configuration GCP
```yaml
REGISTRY: europe-west1-docker.pkg.dev
PROJECT_ID: skillforge-ai-mvp-25
REGION: europe-west1
REPOSITORY: skillforge-docker-repo-staging
```

### Optimisations Build
```yaml
NODE_OPTIONS: --max-old-space-size=4096
VITE_BUILD_CHUNK_SIZE_LIMIT: 2000
VITE_BUILD_ROLLUP_OPTIONS_EXTERNAL: true
```

### Cache
```yaml
PNPM_CACHE_FOLDER: ~/.pnpm-store
```

## Secrets requis

| Secret | Description | Exemple |
|--------|-------------|---------|
| `GCP_PROJECT_ID` | ID du projet GCP | skillforge-ai-mvp-25 |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Provider Workload Identity | projects/123/locations/global/... |
| `GCP_SERVICE_ACCOUNT_EMAIL` | Email du SA | deploy@project.iam.gserviceaccount.com |
| `SLACK_WEBHOOK_URL` | Webhook Slack (optionnel) | https://hooks.slack.com/... |

## Applications déployées

| Application | Chemin | Service Cloud Run | URL |
|-------------|--------|-------------------|-----|
| Shell | `apps/frontend/shell` | `skillforge-frontend-shell-{env}` | skillforge-ai.emacsah.com |
| Auth | `apps/frontend/auth` | `skillforge-frontend-auth-{env}` | auth.skillforge-ai.emacsah.com |
| Admin | `apps/frontend/admin` | `skillforge-frontend-admin-{env}` | admin.skillforge-ai.emacsah.com |
| Company | `apps/frontend/company` | `skillforge-frontend-company-{env}` | company.skillforge-ai.emacsah.com |
| Learner | `apps/frontend/learner` | `skillforge-frontend-learner-{env}` | app.skillforge-ai.emacsah.com |

## Optimisations

### Cache Strategy
1. **Dependencies cache** - pnpm store (clé: hash pnpm-lock.yaml)
2. **Build cache** - Vite build outputs (clé: hash source + deps)
3. **Docker layer cache** - Artifact Registry

### Détection des changements
- Utilise `dorny/paths-filter` pour détecter les fichiers modifiés
- Rebuild uniquement les apps impactées
- Rebuild automatique si packages partagés modifiés

### Build optimization
- Parallel builds avec matrix strategy
- Chunk size optimization (2000 KB)
- Code splitting automatique
- Tree shaking activé

## Configuration Cloud Run

### Ressources
```yaml
CPU: 2 vCPU
Memory: 1 Gi
Min instances: 0
Max instances: 15
Concurrency: 100
```

### Réseau
```yaml
Ingress: internal-and-cloud-load-balancing
Egress: private-ranges-only
VPC Connector: Enabled
```

### Labels
```yaml
app: skillforge-frontend
component: {app-name}
environment: {staging|production}
version: {git-commit-hash}
```

## Troubleshooting

### Build échoue avec erreur de mémoire
**Solution**: Augmenter `NODE_OPTIONS --max-old-space-size`

### Tests timeout
**Solution**: Augmenter le timeout dans vitest.config.ts

### Image Docker trop volumineuse
**Solutions**:
- Vérifier les fichiers .dockerignore
- Optimiser les dépendances
- Utiliser multi-stage build

### Déploiement 403 Forbidden
**Solutions**:
- Vérifier Workload Identity Federation
- Vérifier les permissions du Service Account
- Vérifier l'ingress Cloud Run

### Styles CSS manquants en production
**Solutions**:
- Vérifier tailwind.config.js
- Vérifier postcss.config.js
- Vérifier l'import de global.css

## Monitoring

### Logs
- GitHub Actions: https://github.com/{repo}/actions
- Cloud Logging: Console GCP > Logging > Logs Explorer
- Cloud Run: Console GCP > Cloud Run > Service > Logs

### Métriques
- Déploiement duration: GitHub Actions summary
- Build time: Job logs
- Test coverage: Vitest report
- Docker build time: Docker job logs

## Commandes manuelles

### Déclencher un déploiement manuel
```bash
gh workflow run frontend-deploy.yml \
  -f environment=staging \
  -f apps=shell,auth \
  -f force_rebuild=true
```

### Vérifier le statut du dernier déploiement
```bash
gh run list --workflow=frontend-deploy.yml --limit 5
```

### Voir les logs d'un déploiement
```bash
gh run view {run-id} --log
```

## Rollback

En cas de problème en production:

1. **Rollback Cloud Run**:
```bash
gcloud run services update-traffic skillforge-frontend-shell-production \
  --to-revisions=skillforge-frontend-shell-production-{previous-hash}=100
```

2. **Ou redéployer une version précédente**:
```bash
git revert {commit-hash}
git push origin main
```

## Checklist de déploiement

Avant de merger vers main:
- [ ] Tests passent en local
- [ ] Build réussit en staging
- [ ] Application testée en staging
- [ ] Pas d'erreur dans les logs Cloud Run
- [ ] Métriques normales (latence, erreurs)
- [ ] Approval de la Pull Request

## Contact

Pour toute question sur ce workflow:
- DevOps Team
- Documentation complète: [Workflows README](../README.md)
