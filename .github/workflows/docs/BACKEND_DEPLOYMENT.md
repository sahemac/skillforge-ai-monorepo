# Backend Services Deployment Workflow

## Vue d'ensemble

Ce workflow gère le déploiement automatisé de tous les services backend de SkillForge AI sur Google Cloud Run avec migration de base de données.

**Fichier**: `backend-deploy-optimized.yml`

## Déclencheurs

### Push automatique
- Branches: `main`, `develop`
- Chemins surveillés:
  - `apps/backend/user-service/**`
  - `apps/backend/company-service/**`
  - `.github/workflows/backend-deploy.yml`

### Pull Request
- Branches cibles: `main`, `develop`
- Chemins surveillés: Identiques au push

### Déclenchement manuel (`workflow_dispatch`)
Paramètres disponibles:
- **environment**: staging ou production (défaut: staging)
- **services**: Liste de services séparés par virgule ou "all" (défaut: all)
- **run_migrations**: Exécuter les migrations de base de données (défaut: true)

## Architecture du Workflow

### Phase 1: Setup & Détection

#### Job: `setup`
Détecte les changements et prépare la matrice de déploiement

**Outputs**:
- `user-service`, `company-service`: Services modifiés (true/false)
- `matrix`: Matrice de services à déployer
- `environment`: staging ou production
- `run_migrations`: Exécuter migrations (true/false)
- `cache-key`: Clé de cache unifiée
- `deploy-needed`: Déploiement nécessaire (true/false)

**Étapes clés**:
1. Détection des fichiers modifiés (dorny/paths-filter)
2. Détermination de l'environnement (main=production, autres=staging)
3. Construction de la matrice de services
4. Génération de clé de cache unifiée

### Phase 2: Assurance Qualité Parallèle

#### Job: `security-and-quality`
Exécute tests de sécurité et qualité de code en parallèle

**Services Docker intégrés**:
- PostgreSQL 15 (port 5432)
- Redis 7 (port 6379)

**Scans de sécurité parallèles**:
1. **Bandit** - Analyse de sécurité Python
2. **Safety** - Vérification des vulnérabilités de dépendances
3. **Semgrep** - Analyse statique de code

**Vérifications qualité parallèles**:
1. **Black** - Auto-formatage du code
2. **Flake8** - Linting PEP8
3. **MyPy** - Vérification de types

**Tests unitaires**:
- Pytest avec couverture de code
- Upload vers Codecov

### Phase 3: Migration de Base de Données

#### Job: `database-migration`
Exécute les migrations Alembic sur Cloud SQL

**Dépendances**: security-and-quality

**Configuration**:
- Cloud SQL Proxy pour connexion sécurisée
- Variables d'environnement chiffrées via Secret Manager
- Timeout: 15 minutes
- Retry automatique en cas d'échec

**Étapes**:
1. Authentification GCP avec Workload Identity
2. Récupération des secrets (DATABASE_URL, POSTGRES_PASSWORD, etc.)
3. Démarrage du Cloud SQL Proxy
4. Exécution migrations Alembic avec stratégie de retry
5. Vérification post-migration

### Phase 4: Build & Déploiement

#### Job: `build-and-deploy`
Construction et déploiement des images Docker

**Dépendances**: database-migration

**Optimisations Docker**:
- Multi-stage builds
- Cache de layers via Artifact Registry
- Images optimisées Alpine Linux
- Health checks intégrés

**Configuration Cloud Run**:
```yaml
CPU: 2 vCPU
Memory: 2 Gi
Min instances: 0
Max instances: 10
Concurrency: 80
Timeout: 600s (10 min)
CPU Boost: Enabled
Execution Environment: gen2
```

**Variables d'environnement automatiques**:
- ENVIRONMENT
- SERVICE_NAME
- CLOUD_SQL_CONNECTION_NAME
- REDIS_HOST
- Secrets depuis Secret Manager

**Health Checks avancés**:
- Endpoint `/health` avec retry (max 15 tentatives)
- Vérification de la connectivité Cloud SQL
- Test des endpoints API critiques
- Validation des métriques de performance

### Phase 5: Post-Déploiement

#### Job: `smoke-tests` (si configuré)
Tests de fumée automatiques sur le service déployé

#### Job: `deployment-summary`
Génération du rapport de déploiement

**Métriques incluses**:
- Services déployés
- Durée de build/déploiement
- Statut des tests
- Résultats des scans de sécurité
- URLs des services

## Variables d'environnement

### Configuration GCP
```yaml
REGISTRY: europe-west1-docker.pkg.dev
PROJECT_ID: skillforge-ai-mvp-25
REGION: europe-west1
REPOSITORY: skillforge-docker-repo-staging
PYTHON_VERSION: '3.11'
```

### Secrets requis

| Secret | Description | Exemple |
|--------|-------------|---------|
| `GCP_PROJECT_ID` | ID du projet GCP | skillforge-ai-mvp-25 |
| `GCP_WIF_PROVIDER` | Workload Identity Provider | projects/123/.../providers/github |
| `GCP_CICD_SERVICE_ACCOUNT` | Email du SA CI/CD | deploy@project.iam.gserviceaccount.com |
| `DATABASE_URL` | URL PostgreSQL (Secret Manager) | postgresql+asyncpg://... |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | Stored in Secret Manager |
| `SMTP_PASSWORD` | Mot de passe SMTP | Stored in Secret Manager |
| `SLACK_WEBHOOK_URL` | Webhook Slack (optionnel) | https://hooks.slack.com/... |

### Secrets Cloud SQL

Tous les secrets de connexion sont stockés dans Google Secret Manager:
- `DATABASE_URL` - URL complète de connexion
- `POSTGRES_PASSWORD` - Mot de passe base de données
- `SMTP_PASSWORD` - Mot de passe email
- Autres secrets métier spécifiques aux services

## Services déployés

| Service | Chemin | Port | Cloud Run Service | API Endpoint |
|---------|--------|------|-------------------|--------------|
| User Service | `apps/backend/user-service` | 8000 | `skillforge-user-service-{env}` | api.skillforge-ai.com/users |
| Company Service | `apps/backend/company-service` | 8001 | `skillforge-company-service-{env}` | api.skillforge-ai.com/companies |

## Migrations de Base de Données

### Stratégie Alembic

Le workflow utilise Alembic pour les migrations:

1. **Génération automatique** (en développement):
```bash
alembic revision --autogenerate -m "Description"
```

2. **Application des migrations**:
```bash
alembic upgrade head
```

3. **Rollback** (si nécessaire):
```bash
alembic downgrade -1  # Revenir d'une migration
```

### Gestion des erreurs de migration

**Retry automatique**: 3 tentatives avec délai exponentiel
**Logging structuré**: Tous les logs envoyés à Cloud Logging
**Validation post-migration**: Vérification de la cohérence des schémas

### Bonnes pratiques

- Toujours tester les migrations en staging avant production
- Créer des migrations réversibles (up/down)
- Sauvegarder la base avant les migrations critiques
- Documenter les migrations complexes

## Optimisations

### Stratégie de Cache

1. **Unified cache** - Dépendances Python partagées
   - Clé: `{OS}-unified-{PYTHON_VERSION}-{requirements-hash}`
   - Partagé entre tous les services

2. **Docker layer cache** - Artifact Registry
   - Cache des layers intermédiaires
   - Réutilisation entre builds

3. **pip cache** - `~/.cache/pip`
   - Cache des packages téléchargés

### Exécution parallèle

- Scans de sécurité (Bandit + Safety + Semgrep)
- Vérifications qualité (Black + Flake8 + MyPy)
- Builds Docker multi-services avec matrix strategy

### Optimisations Cloud Run

- Gen2 execution environment (meilleure performance)
- CPU boost au démarrage
- Connexion Cloud SQL via Unix socket (plus rapide que TCP)
- VPC Connector pour réseau privé

## Troubleshooting

### Migration échoue avec "relation already exists"

**Cause**: Migration déjà appliquée ou schéma désynchronisé

**Solution**:
```bash
# Vérifier l'état actuel
alembic current

# Marquer comme appliquée sans exécuter
alembic stamp head

# Ou rollback et réessayer
alembic downgrade base
alembic upgrade head
```

### Cloud SQL Connection timeout

**Causes possibles**:
- Cloud SQL Proxy pas démarré
- Permissions IAM insuffisantes
- Instance Cloud SQL arrêtée

**Solutions**:
1. Vérifier que le Cloud SQL Proxy est démarré
2. Vérifier les permissions du service account:
   ```bash
   gcloud projects get-iam-policy skillforge-ai-mvp-25 \
     --filter="bindings.members:serviceAccount:sa-{service}-staging@*"
   ```
3. Vérifier l'état de l'instance:
   ```bash
   gcloud sql instances describe skillforge-pg-instance-staging
   ```

### Tests échouent avec "ModuleNotFoundError"

**Solution**: Vérifier que toutes les dépendances sont dans requirements.txt
```bash
pip freeze > requirements.txt
```

### Build Docker échoue avec "No space left on device"

**Solution**: L'image est trop volumineuse
- Optimiser les layers Docker
- Utiliser .dockerignore
- Nettoyer les caches dans le Dockerfile

### Service ne démarre pas après déploiement

**Vérifications**:
1. Logs Cloud Run:
   ```bash
   gcloud run services logs read skillforge-{service}-staging \
     --region=europe-west1 --limit=50
   ```

2. Variables d'environnement correctes:
   ```bash
   gcloud run services describe skillforge-{service}-staging \
     --region=europe-west1 --format="value(spec.template.spec.containers[0].env)"
   ```

3. Health check endpoint accessible:
   ```bash
   curl https://{service-url}/health
   ```

### Erreur 403 sur les secrets

**Cause**: Service account n'a pas accès à Secret Manager

**Solution**:
```bash
# Accorder l'accès Secret Manager
gcloud secrets add-iam-policy-binding DATABASE_URL \
  --member="serviceAccount:sa-{service}-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Monitoring

### Logs

**GitHub Actions**:
```bash
gh run list --workflow=backend-deploy-optimized.yml --limit 10
gh run view {run-id} --log
```

**Cloud Logging**:
```bash
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=skillforge-{service}-staging" \
  --limit=50 --format=json
```

**Cloud SQL Logs**:
```bash
gcloud logging read "resource.type=cloudsql_database \
  AND logName=projects/skillforge-ai-mvp-25/logs/cloudsql.googleapis.com%2Fpostgres.log" \
  --limit=20
```

### Métriques

**Durée de déploiement**: GitHub Actions summary
**Temps de build**: Job logs "build-and-deploy"
**Couverture de code**: Codecov dashboard
**Scans de sécurité**: SARIF reports dans Security tab

### Alertes

Les alertes sont envoyées via:
- Slack (si configuré)
- Email GitHub
- Cloud Monitoring (pour métriques GCP)

## Commandes manuelles

### Déclencher un déploiement manuel

```bash
gh workflow run backend-deploy-optimized.yml \
  -f environment=staging \
  -f services=user-service,company-service \
  -f run_migrations=true
```

### Vérifier le statut

```bash
# Derniers déploiements
gh run list --workflow=backend-deploy-optimized.yml --limit 5

# Détails d'un déploiement
gh run view {run-id}

# Logs d'un job spécifique
gh run view {run-id} --log --job={job-id}
```

### Exécuter migration manuellement

```bash
# Via Cloud Run Jobs (recommandé)
gcloud run jobs execute alembic-migration-job \
  --region=europe-west1

# Via Cloud SQL Proxy local (développement)
./cloud-sql-proxy skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging &
alembic upgrade head
```

## Rollback

### Rollback Cloud Run

```bash
# Lister les révisions
gcloud run revisions list \
  --service=skillforge-user-service-staging \
  --region=europe-west1

# Rollback vers révision précédente
PREVIOUS_REVISION=$(gcloud run revisions list \
  --service=skillforge-user-service-staging \
  --region=europe-west1 \
  --format="value(metadata.name)" \
  --sort-by="~metadata.creationTimestamp" \
  --limit=2 | tail -1)

gcloud run services update-traffic skillforge-user-service-staging \
  --region=europe-west1 \
  --to-revisions="${PREVIOUS_REVISION}=100"
```

### Rollback Base de Données

```bash
# Downgrade d'une migration
alembic downgrade -1

# Downgrade vers version spécifique
alembic downgrade {revision_id}

# Vérifier la version actuelle
alembic current
```

## Checklist de déploiement

Avant de merger vers main:
- [ ] Tests passent en local
- [ ] Migrations testées en staging
- [ ] Scans de sécurité sans critiques
- [ ] Build réussit en staging
- [ ] Services déployés et fonctionnels en staging
- [ ] Pas d'erreur dans les logs Cloud Run
- [ ] Pas d'erreur dans les logs Cloud SQL
- [ ] Health checks passent
- [ ] Performance acceptable (< 500ms)
- [ ] Métriques normales (CPU, mémoire, latence)
- [ ] Backup base de données effectué (pour production)
- [ ] Approval de la Pull Request

## Sécurité

### Secrets Management

- Tous les secrets dans Google Secret Manager
- Rotation automatique des secrets recommandée
- Accès secrets limité aux service accounts spécifiques
- Audit logging activé pour accès secrets

### Network Security

- VPC Connector pour communication privée
- Cloud SQL accessible uniquement via VPC
- Ingress: internal-and-cloud-load-balancing
- Egress: private-ranges-only

### IAM Permissions

Permissions minimales requises par service account:
- `roles/cloudsql.client`
- `roles/secretmanager.secretAccessor`
- `roles/logging.logWriter`
- `roles/monitoring.metricWriter`
- `roles/cloudtrace.agent`

## Contact

Pour toute question sur ce workflow:
- DevOps Team
- Documentation complète: [Workflows README](../README.md)
- Rapports de sécurité: GitHub Security tab
