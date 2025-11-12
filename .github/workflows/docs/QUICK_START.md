# Guide de Démarrage Rapide - CI/CD

Guide rapide pour les développeurs sur le processus CI/CD de SkillForge AI.

## TL;DR

```bash
# 1. Créer une branche depuis develop
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Développer et committer
git add .
git commit -m "feat: add new feature"

# 3. Pousser et créer une PR
git push origin feature/my-feature
gh pr create --base develop --title "feat: add new feature"

# 4. Attendre les checks ✅
# 5. Merge → Auto-deploy vers staging
# 6. Tester en staging
# 7. Merge vers main (avec approbation) → Production
```

## Workflow de développement

### 1. Créer une Pull Request

**Depuis develop uniquement !**

```bash
# Créer une branche feature
git checkout -b feature/amazing-feature

# Faire vos changements...

# Commit avec format Conventional Commits
git commit -m "feat(api): add user profile endpoint"
```

**Format des commits** (obligatoire):
- `feat: nouvelle fonctionnalité`
- `fix: correction de bug`
- `docs: documentation`
- `style: formatting`
- `refactor: refactorisation`
- `test: ajout de tests`
- `chore: tâches diverses`

### 2. Attendre les checks automatiques

La PR déclenche automatiquement:

- ✅ **PR Validation** (< 1 min)
  - Titre en format Conventional Commits
  - Description présente
  - Taille raisonnable (< 1000 lignes)

- ✅ **Backend Tests** (5-8 min)
  - Tests avec PostgreSQL + Redis
  - Scans de sécurité (Bandit, Safety)
  - Code quality (Black, Flake8, MyPy)

- ✅ **Frontend Tests** (4-6 min)
  - Tests Vitest
  - Linting ESLint
  - Type checking TypeScript
  - Build production

- ✅ **Security Scan** (2-3 min)
  - Trivy vulnerability scan
  - SARIF report

**Total**: ~10-15 minutes

### 3. Merge vers develop

Une fois tous les checks passés et la PR approuvée:

```bash
# Via GitHub UI: cliquer "Merge pull request"

# Ou via CLI
gh pr merge --squash
```

**Résultat**: Déploiement automatique vers **staging** ! 🚀

### 4. Validation en staging

Après le merge, le workflow `deploy-staging-auto` se déclenche:

**Étapes** (15-25 min):
1. Détection des changements
2. Déploiement backend/frontend
3. Smoke tests
4. E2E tests
5. Résumé + notifications Slack

**URLs staging**:
- Frontend: https://skillforge-ai.emacsah.com
- User API: https://skillforge-user-service-staging-721427084268.europe-west1.run.app
- Company API: https://skillforge-company-service-staging-721427084268.europe-west1.run.app

**Tester manuellement**:
```bash
# Health check
curl https://skillforge-ai.emacsah.com/health

# Test API
curl https://skillforge-user-service-staging-721427084268.europe-west1.run.app/api/v1/users/

# Consulter les logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=skillforge-frontend-shell-staging" \
  --limit=20
```

### 5. Déploiement en production

**Option A: Déploiement standard** (recommandé)

```bash
# 1. Créer PR depuis develop vers main
gh pr create --base main --title "release: v1.2.3"

# 2. Attendre approbation
# 3. Merge

# 4. Le workflow deploy-production.yml se déclenche
# ⏸ Nécessite approbation manuelle via GitHub Environments
```

**Option B: Déploiement canary** (pour changements critiques)

```bash
# 1. S'assurer que le code est sur main

# 2. Déclencher le canary
gh workflow run canary-deployment.yml -f service=shell

# 3. Approuver chaque étape (10% → 50% → 100%)
```

## Commandes rapides

### Vérifier le statut des workflows

```bash
# Workflows en cours
gh run list --limit 5

# Détails d'un workflow
gh run view <run-id>

# Logs d'un workflow
gh run view <run-id> --log

# Annuler un workflow
gh run cancel <run-id>
```

### Voir les déploiements

```bash
# Services Cloud Run
gcloud run services list --region=europe-west1

# Révisions d'un service
gcloud run revisions list --service=skillforge-frontend-shell-staging \
  --region=europe-west1

# Logs en temps réel
gcloud logging tail "resource.type=cloud_run_revision"
```

### Rollback

```bash
# Script automatique
./scripts/canary-rollback.sh skillforge-frontend-shell-production

# Ou manuel
gcloud run services update-traffic skillforge-frontend-shell-production \
  --region=europe-west1 \
  --to-revisions=PREVIOUS_REVISION=100
```

## Troubleshooting

### ❌ PR checks échouent

**Tests backend échouent**:
```bash
# Lancer tests en local
cd apps/backend/user-service
pip install -r requirements.txt
pytest tests/
```

**Tests frontend échouent**:
```bash
# Lancer tests en local
cd apps/frontend/shell
pnpm install
pnpm test
pnpm run type-check
```

**Linting échoue**:
```bash
# Backend
cd apps/backend/user-service
black app/
flake8 app/

# Frontend
cd apps/frontend/shell
pnpm run lint --fix
```

### ❌ Déploiement staging échoue

1. **Consulter les logs du workflow**:
   ```bash
   gh run list --workflow=deploy-staging-auto.yml --limit 3
   gh run view <run-id> --log
   ```

2. **Vérifier les logs Cloud Run**:
   ```bash
   gcloud run services logs read skillforge-frontend-shell-staging \
     --region=europe-west1 \
     --limit=50
   ```

3. **Vérifier le service**:
   ```bash
   gcloud run services describe skillforge-frontend-shell-staging \
     --region=europe-west1
   ```

### ❌ E2E tests échouent

```bash
# Lancer E2E tests en local
cd apps/frontend/shell
pnpm exec playwright install
pnpm exec playwright test

# Voir le rapport
pnpm exec playwright show-report
```

### ⏸ Workflow bloqué sur approbation

1. Aller sur Actions → Workflow en cours
2. Cliquer sur le job nécessitant approbation
3. "Review deployments"
4. Approuver ou rejeter

## Bonnes pratiques

### ✅ À FAIRE

- **Toujours** partir de `develop` pour une nouvelle branche
- **Tester en local** avant de push
- **Écrire des tests** pour les nouvelles features
- **Suivre Conventional Commits** pour les messages
- **Petites PRs** (< 500 lignes préférable)
- **Description détaillée** dans les PRs
- **Surveiller** le déploiement staging
- **Tester manuellement** en staging avant prod

### ❌ À ÉVITER

- ❌ Commit direct sur `develop` ou `main`
- ❌ PR géantes (> 1000 lignes)
- ❌ Messages de commit vagues ("fix stuff", "wip")
- ❌ Merge sans attendre les checks
- ❌ Déploiement prod vendredi soir
- ❌ Sauter les tests manuels en staging

## Cheat Sheet

### Git Flow

```bash
# Synchroniser avec develop
git checkout develop
git pull origin develop

# Créer feature branch
git checkout -b feature/my-feature

# Committer
git add .
git commit -m "feat: my feature"

# Push et créer PR
git push origin feature/my-feature
gh pr create --base develop

# Après merge, supprimer la branche
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

### Conventional Commits

```bash
# Feature
git commit -m "feat(api): add user search endpoint"

# Bug fix
git commit -m "fix(auth): resolve token expiration issue"

# Documentation
git commit -m "docs: update API documentation"

# Refactoring
git commit -m "refactor(db): optimize user query"

# Breaking change
git commit -m "feat!: redesign user API
BREAKING CHANGE: User API endpoints have been redesigned"
```

### Workflow Commands

```bash
# Voir workflows disponibles
gh workflow list

# Lancer un workflow
gh workflow run <workflow-name>

# Voir runs récents
gh run list --limit 10

# Watch un run
gh run watch <run-id>

# Télécharger artifacts
gh run download <run-id>
```

## FAQ

**Q: Combien de temps prend un déploiement vers staging ?**
A: 15-25 minutes (détection + déploiement + tests)

**Q: Combien de temps prend un déploiement vers production ?**
A: 20-30 minutes + temps d'approbation manuelle

**Q: Que faire si les tests passent en local mais échouent en CI ?**
A: Vérifier les variables d'environnement, les versions de dépendances, et consulter les logs détaillés du workflow.

**Q: Puis-je skip les tests ?**
A: Non, tous les tests doivent passer pour merger. C'est une protection importante.

**Q: Quand utiliser le déploiement canary ?**
A: Pour les changements critiques, les refactorings majeurs, ou après une longue période sans déploiement.

**Q: Comment rollback un déploiement ?**
A: Utiliser le script `./scripts/canary-rollback.sh` ou la commande gcloud pour router le trafic vers la révision précédente.

**Q: Les déploiements staging peuvent-ils casser la production ?**
A: Non, staging et production sont complètement isolés.

## Ressources

- [Architecture CI/CD](./CI_CD_ARCHITECTURE.md)
- [Branch Protection](./BRANCH_PROTECTION.md)
- [Canary Deployment](./CANARY_DEPLOYMENT.md)
- [Backend Deployment](./BACKEND_DEPLOYMENT.md)
- [Frontend Deployment](./FRONTEND_DEPLOYMENT.md)

## Support

- **Slack**: #devops channel
- **Issues**: GitHub avec label `ci-cd`
- **Documentation**: `.github/workflows/docs/`
